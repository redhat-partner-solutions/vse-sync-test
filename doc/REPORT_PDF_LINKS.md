# Clickable GitHub links in the synchronization test report PDF

The PDF **Test Results** section includes a *test identifier* row. That row shows the same human-readable name as today; the name is also a **hyperlink** to the test’s directory on GitHub (`…/tree/main/tests/sync/…`).

## How it works

1. **JUnit** (`testdrive.junit.create`) adds a property `test_directory_url` on each testcase: the canonical test id URL with any query string removed (GitHub tree URL for the test case directory).
2. **Report generator** (`vse-sync-test-report`, module `testdrive.asciidoc`) renders the *test identifier* cell as AsciiDoc `link:url[display name]`, so **asciidoctor-pdf** produces a clickable link. The visible text is unchanged (`test_id` / prettified display name).

## Container image

`Containerfile` copies the patched `asciidoc.py` from `contrib/vse-sync-test-report/src/testdrive/asciidoc.py` over the clone of `vse-sync-test-report`, so images built from this repository get the behavior without a separate checkout step.

## Local runs (`cmd/e2e.sh`)

If `REPORTGENPATH` points to a normal clone of [vse-sync-test-report](https://github.com/redhat-partner-solutions/vse-sync-test-report), copy the patched file over the upstream module:

```bash
cp contrib/vse-sync-test-report/src/testdrive/asciidoc.py \
   "$REPORTGENPATH/src/testdrive/asciidoc.py"
```

Alternatively, open a pull request on `vse-sync-test-report` with the same change so the overlay in `Containerfile` can be dropped once merged.

## Upstream

The canonical copy of the AsciiDoc generator lives in `vse-sync-test-report`. The file under `contrib/` tracks the intended upstream content for review and PRs.
