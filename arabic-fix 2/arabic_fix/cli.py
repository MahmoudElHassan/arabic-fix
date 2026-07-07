"""CLI entry point — `arabic-fix` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .fixer import fix, fix_report, FixOptions


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="arabic-fix",
        description=(
            "Fix Arabic text in files: letter-shape, BiDi-reorder, normalize. "
            "Reads UTF-8, writes UTF-8."
        ),
    )
    p.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files to fix. Use '-' or omit to read from stdin.",
    )
    p.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file. Only valid with a single input file. "
             "If omitted with one input, write in place.",
    )
    p.add_argument("--no-shape", action="store_true", help="Skip letter shaping.")
    p.add_argument("--no-bidi", action="store_true", help="Skip BiDi reordering.")
    p.add_argument(
        "--no-normalize",
        action="store_true",
        help="Skip Unicode normalization.",
    )
    p.add_argument(
        "--normalize-form",
        default="NFC",
        choices=["NFC", "NFD", "NFKC", "NFKD"],
        help="Unicode normalization form (default NFC).",
    )
    p.add_argument(
        "--bidi-base-dir",
        default="rtl",
        choices=["rtl", "ltr"],
        help="Base direction for BiDi reorder (default rtl).",
    )
    p.add_argument(
        "--no-ligatures",
        action="store_true",
        help="Disable reshape ligatures (e.g. لا, ﷲ).",
    )
    p.add_argument(
        "--report",
        action="store_true",
        help="Print a JSON report per file (what was shaped, reordered, "
             "normalized) to stderr.",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any file would change. Useful in CI to "
             "enforce Arabic text is already fixed.",
    )
    p.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default utf-8).",
    )
    return p


def _process(text: str, opts: FixOptions) -> str:
    return fix(text, **opts.__dict__)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    opts = FixOptions(
        shape=not args.no_shape,
        bidi=not args.no_bidi,
        normalize_text=not args.no_normalize,
        normalize_form=args.normalize_form,
        bidi_base_dir=args.bidi_base_dir,
        ligatures=not args.no_ligatures,
    )

    if not args.paths or (len(args.paths) == 1 and str(args.paths[0]) == "-"):
        # stdin → stdout
        text = sys.stdin.read()
        out = _process(text, opts)
        sys.stdout.write(out)
        return 0

    if len(args.paths) > 1 and args.output:
        print("error: --output can only be used with a single input file.",
              file=sys.stderr)
        return 2

    exit_code = 0
    for path in args.paths:
        try:
            original = path.read_text(encoding=args.encoding)
        except OSError as exc:
            print(f"error: cannot read {path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        report = fix_report(original, **opts.__dict__)

        if args.report:
            import json
            payload = {
                "path": str(path),
                "changed": report.changed,
                "shaped": report.shaped,
                "bidi_reordered": report.bidi_reordered,
                "normalized": report.normalized,
                "contained_arabic": report.contained_arabic,
                "warnings": report.warnings,
            }
            print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)

        if args.check:
            if report.changed:
                print(f"would change: {path}", file=sys.stderr)
                exit_code = 1
            continue

        if not report.changed:
            continue

        target = args.output if args.output else path
        try:
            target.write_text(report.output, encoding=args.encoding)
        except OSError as exc:
            print(f"error: cannot write {target}: {exc}", file=sys.stderr)
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
