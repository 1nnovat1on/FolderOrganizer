# FolderOrganizer

A local-only Windows desktop utility for organizing **visible, top-level regular files** into folders named for their extensions.

## Privacy and safety

- Runs entirely on your computer: no web requests, accounts, email, OAuth, telemetry, analytics, or credentials.
- It previews eligible files before changing anything.
- Moving files requires an explicit confirmation dialog.
- Directories, hidden files, and existing destination folders are excluded from the preview and are never moved.
- Name collisions never overwrite an existing file; a suffix such as `report (1).txt` is used.
- Each completed run writes `.folderorganizer-last-run.json` in the chosen folder with UTC timestamp plus original and destination paths. **Undo Last Run** uses it to restore files without overwriting existing files.

## Use

1. Run `python launcher.py`, or build the Windows executable as described below.
2. Choose a folder.
3. Review the extension-grouped preview.
4. Select **Organize Preview** and confirm the move.
5. To revert the most recent completed run for that folder, select **Undo Last Run** and confirm.

## Build a Windows executable

Install the build dependency in your own environment, then run `build_windows.bat`:

```text
python -m pip install -r requirements.txt
build_windows.bat
```

The executable is generated at `dist\FolderOrganizer.exe`. Generated binaries and build folders are intentionally ignored by Git.

## Test and verify

```text
python -m unittest discover -s tests -v
python -m compileall -q folder_organizer launcher.py
```

## Limitations

- Only the selected folder's immediate files are considered; subfolders are not scanned or reorganized.
- Files without an extension go to `no_extension`.
- Undo applies only to the latest manifest in the selected folder. If a destination is missing or an original path is now occupied, undo skips that record rather than overwriting data; the manifest remains for a later retry.
- If a move fails mid-run (for example, because another program locks a file), completed moves remain recorded in the manifest only after the run completes. Resolve the lock and review the folder before trying again.

## License

MIT. See [LICENSE](LICENSE).
