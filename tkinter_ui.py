"""Tkinter user interface for the 3do23d converter."""

from __future__ import annotations

import contextlib
import io
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

import _3do_v3_icr2 as converter


class QueueWriter(io.TextIOBase):
    """File-like writer that forwards text to a thread-safe queue."""

    def __init__(self, output_queue: queue.Queue[str]) -> None:
        self.output_queue = output_queue

    def writable(self) -> bool:
        return True

    def write(self, text: str) -> int:
        if text:
            self.output_queue.put(text)
        return len(text)

    def flush(self) -> None:
        return None


class ConverterApp(tk.Tk):
    """Small desktop UI for converting ICR2 3DO files to N3 3D files."""

    def __init__(self) -> None:
        super().__init__()
        self.title("3do23d Converter")
        self.minsize(680, 520)

        self.output_queue: queue.Queue[str] = queue.Queue()
        self.worker: threading.Thread | None = None

        self.conversion_mode = tk.StringVar(value="file")
        self.input_file = tk.StringVar()
        self.input_folder = tk.StringVar()
        self.output_file = tk.StringVar()
        self.tolerance = tk.StringVar(value="1")
        self.sort_vertices = tk.BooleanVar(value=False)
        self.combine_data_with_list = tk.BooleanVar(value=False)
        self.generate_missing_planes = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Ready")

        self._build_ui()
        self.after(100, self._drain_output_queue)

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=16)
        main.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(7, weight=1)

        mode = ttk.LabelFrame(main, text="Conversion mode", padding=8)
        mode.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        ttk.Radiobutton(mode, text="Single .3DO file", variable=self.conversion_mode, value="file", command=self._update_mode).pack(side="left")
        ttk.Radiobutton(mode, text="All .3DO files in a folder", variable=self.conversion_mode, value="folder", command=self._update_mode).pack(side="left", padx=(16, 0))

        self.input_file_label = ttk.Label(main, text="Input .3DO file")
        self.input_file_label.grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.input_file_entry = ttk.Entry(main, textvariable=self.input_file)
        self.input_file_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 8))
        self.input_file_button = ttk.Button(main, text="Browse...", command=self._browse_input)
        self.input_file_button.grid(row=1, column=2, pady=(0, 8))

        self.input_folder_label = ttk.Label(main, text="Input folder")
        self.input_folder_label.grid(row=2, column=0, sticky="w", pady=(0, 8))
        self.input_folder_entry = ttk.Entry(main, textvariable=self.input_folder)
        self.input_folder_entry.grid(row=2, column=1, sticky="ew", padx=8, pady=(0, 8))
        self.input_folder_button = ttk.Button(main, text="Browse...", command=self._browse_folder)
        self.input_folder_button.grid(row=2, column=2, pady=(0, 8))

        self.output_file_label = ttk.Label(main, text="Output .3D file")
        self.output_file_label.grid(row=3, column=0, sticky="w", pady=(0, 8))
        self.output_file_entry = ttk.Entry(main, textvariable=self.output_file)
        self.output_file_entry.grid(row=3, column=1, sticky="ew", padx=8, pady=(0, 8))
        self.output_file_button = ttk.Button(main, text="Save as...", command=self._browse_output)
        self.output_file_button.grid(row=3, column=2, pady=(0, 8))

        ttk.Label(main, text="Tolerance").grid(row=4, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(main, textvariable=self.tolerance, width=12).grid(row=4, column=1, sticky="w", padx=8, pady=(0, 8))

        options = ttk.LabelFrame(main, text="Options", padding=8)
        options.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        options.columnconfigure(0, weight=1)
        ttk.Checkbutton(options, text="Sort vertices to the beginning of the output file", variable=self.sort_vertices).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(options, text="Combine DATA statements into LIST statements", variable=self.combine_data_with_list).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(options, text="Generate inline vertices for missing BSP/FACE planes", variable=self.generate_missing_planes).grid(row=2, column=0, sticky="w")

        actions = ttk.Frame(main)
        actions.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        self.convert_button = ttk.Button(actions, text="Convert", command=self._start_conversion)
        self.convert_button.pack(side="left")
        ttk.Button(actions, text="Clear log", command=self._clear_log).pack(side="left", padx=8)
        ttk.Label(actions, textvariable=self.status).pack(side="right")

        self.log = scrolledtext.ScrolledText(main, height=14, state="disabled", wrap="word")
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew")
        self._update_mode()

    def _browse_input(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select ICR2 3DO file",
            filetypes=(("3DO files", "*.3do *.3DO"), ("All files", "*.*")),
        )
        if filename:
            self.input_file.set(filename)
            if not self.output_file.get():
                self.output_file.set(str(Path(filename).with_suffix(".3d")))

    def _browse_folder(self) -> None:
        foldername = filedialog.askdirectory(title="Select folder containing ICR2 3DO files")
        if foldername:
            self.input_folder.set(foldername)

    def _browse_output(self) -> None:
        filename = filedialog.asksaveasfilename(
            title="Choose output 3D file",
            defaultextension=".3d",
            filetypes=(("3D files", "*.3d *.3D"), ("All files", "*.*")),
        )
        if filename:
            self.output_file.set(filename)

    def _start_conversion(self) -> None:
        if self.worker and self.worker.is_alive():
            return

        mode = self.conversion_mode.get()
        try:
            tolerance = float(self.tolerance.get())
        except ValueError:
            messagebox.showerror("Invalid tolerance", "Tolerance must be a number.")
            return

        if mode == "folder":
            input_folder = self.input_folder.get().strip()
            if not input_folder:
                messagebox.showerror("Missing input folder", "Choose an input folder before converting.")
                return
            folder_path = Path(input_folder)
            if not folder_path.is_dir():
                messagebox.showerror("Input folder not found", f"The input folder does not exist:\n{input_folder}")
                return
            input_files = sorted(path for path in folder_path.iterdir() if path.is_file() and path.suffix.lower() == ".3do")
            if not input_files:
                messagebox.showerror("No .3DO files found", f"No .3DO files were found in:\n{input_folder}")
                return
            self._append_log(f"Starting folder conversion for {input_folder} ({len(input_files)} files)\n")
            worker_args = (input_files, tolerance, self._get_options())
            worker_target = self._convert_folder
        else:
            input_file = self.input_file.get().strip()
            output_file = self.output_file.get().strip() or None
            if not input_file:
                messagebox.showerror("Missing input file", "Choose an input .3DO file before converting.")
                return
            if not Path(input_file).is_file():
                messagebox.showerror("Input file not found", f"The input file does not exist:\n{input_file}")
                return
            self._append_log(f"Starting conversion for {input_file}\n")
            worker_args = (input_file, output_file, tolerance, self._get_options())
            worker_target = self._convert

        self.convert_button.configure(state="disabled")
        self.status.set("Converting...")
        self.worker = threading.Thread(target=worker_target, args=worker_args, daemon=True)
        self.worker.start()

    def _get_options(self) -> dict[str, bool]:
        return {
            "sort_vertices": self.sort_vertices.get(),
            "combine_data_with_list": self.combine_data_with_list.get(),
            "generate_missing_planes": self.generate_missing_planes.get(),
        }

    def _convert(
        self,
        input_file: str,
        output_file: str | None,
        tolerance: float,
        options: dict[str, bool],
    ) -> None:
        writer = QueueWriter(self.output_queue)
        try:
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                converter.convert_3do23d(
                    filename=input_file,
                    output_file=output_file,
                    tolerance=tolerance,
                    sort_vertices=options["sort_vertices"],
                    combine_data_with_list=options["combine_data_with_list"],
                    generate_missing_planes=options["generate_missing_planes"],
                )
        except Exception as exc:  # noqa: BLE001 - surface converter errors in the UI.
            self.output_queue.put(f"\nConversion failed: {exc}\n")
            self.output_queue.put("__STATUS__:ERROR")
        else:
            self.output_queue.put("\nConversion finished successfully.\n")
            self.output_queue.put("__STATUS__:DONE")

    def _convert_folder(
        self,
        input_files: list[Path],
        tolerance: float,
        options: dict[str, bool],
    ) -> None:
        writer = QueueWriter(self.output_queue)
        failures = 0
        with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
            for index, input_file in enumerate(input_files, start=1):
                print(f"\n[{index}/{len(input_files)}] Converting {input_file}")
                try:
                    converter.convert_3do23d(
                        filename=str(input_file),
                        output_file=str(input_file.with_suffix(".3d")),
                        tolerance=tolerance,
                        sort_vertices=options["sort_vertices"],
                        combine_data_with_list=options["combine_data_with_list"],
                        generate_missing_planes=options["generate_missing_planes"],
                    )
                except Exception as exc:  # noqa: BLE001 - keep batch conversion running.
                    failures += 1
                    print(f"Conversion failed for {input_file}: {exc}")
        if failures:
            self.output_queue.put(f"\nFolder conversion finished with {failures} failure(s).\n")
            self.output_queue.put("__STATUS__:ERROR")
        else:
            self.output_queue.put("\nFolder conversion finished successfully.\n")
            self.output_queue.put("__STATUS__:DONE_FOLDER")

    def _update_mode(self) -> None:
        if self.conversion_mode.get() == "folder":
            state = "disabled"
            folder_state = "normal"
        else:
            state = "normal"
            folder_state = "disabled"
        for widget in (self.input_file_entry, self.input_file_button, self.output_file_entry, self.output_file_button):
            widget.configure(state=state)
        for widget in (self.input_folder_entry, self.input_folder_button):
            widget.configure(state=folder_state)

    def _drain_output_queue(self) -> None:
        try:
            while True:
                text = self.output_queue.get_nowait()
                if text == "__STATUS__:DONE":
                    self.status.set("Done")
                    self.convert_button.configure(state="normal")
                    messagebox.showinfo("Conversion complete", "The 3DO file was converted successfully.")
                elif text == "__STATUS__:DONE_FOLDER":
                    self.status.set("Done")
                    self.convert_button.configure(state="normal")
                    messagebox.showinfo("Conversion complete", "All 3DO files in the folder were converted successfully.")
                elif text == "__STATUS__:ERROR":
                    self.status.set("Error")
                    self.convert_button.configure(state="normal")
                    messagebox.showerror("Conversion failed", "See the log for details.")
                else:
                    self._append_log(text)
        except queue.Empty:
            pass
        self.after(100, self._drain_output_queue)

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")


def main() -> None:
    app = ConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
