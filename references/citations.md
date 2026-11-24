# Live citations in Word

A manuscript written in Markdown or Quarto and built with pandoc holds its citations as keys (`[@okafor2021]`). Co-authors and journals work in Word, where each citation should be a field of the researcher's reference manager: co-authors can then add references, and the style can change in one step. `scripts/live_citations.py` turns the keys into Zotero fields or EndNote temporary citations; after a refresh in Word they behave as if inserted with the manager's plugin.

## When to convert

- Convert once the text is settled, as the last step before the file goes to co-authors or a journal. From then on the Word file is the master: co-authors edit it, and a rebuild from Markdown would lose their edits. Before any rebuild, compare the Word file with the last build (`check_preservation.py`) and carry its changes into the Markdown first.
- Use the researcher's own manager, one per document. Ask which when it is not known. A file with both kinds of field cannot be updated by either.
- A manuscript written in Word with the plugin already has live citations. Never change text inside a field by hand ([format.md](format.md)).

## What the conversion needs

- A bibliography in CSL JSON with each key's DOI and title (`pandoc refs.bib -t csljson -o refs.json`). For Zotero it can be left out when every key is a Better BibTeX citation key in the library.
- Plain citations: `[@okafor2021]` or `[@okafor2021; @lindqvist2019]`. Locators, prefixes and suffixes (`[@okafor2021, p. 4]`, `[see @okafor2021]`), suppressed authors (`[-@okafor2021]`) and in-text `@okafor2021` stop the conversion. Rewrite them as plain citations, or add them in Word afterwards with the plugin.
- Each cited reference in the library exactly once. A key that matches no item, or matches two (a duplicate), stops the conversion.
- The conversion is all or nothing: when anything stops it, nothing is written and each problem is listed with its line. The script reads the library and never changes it.
- Matching: by citation key first (Zotero), then by DOI, then by title when one side has no DOI. Better BibTeX search does not look in the DOI field and matches its text as one phrase, so the script searches phrases taken from the title and compares the DOIs it gets back. Libraries often hold duplicates; merge them in the manager before converting.

## Zotero

Needs Zotero with the Better BibTeX plugin and the Word plugin, Zotero open, and access to Zotero's local port (127.0.0.1:23119).

```bash
python3 scripts/live_citations.py zotero ms.md --bibliography refs.json -o ms.zotero.md
pandoc ms.zotero.md -o ms.docx                    # the project's own pandoc command, without --citeproc
python3 scripts/live_citations.py prefs ms.docx --style vancouver
```

- `prefs` writes the citation style into the Word file. The style is the last part of its address in the Zotero style repository: `vancouver`, `nature`, `the-lancet`, `american-medical-association`, `new-england-journal-of-medicine`, `bmj`.
- Open the file in Word and click Refresh in the Zotero tab. The placeholders `{Citation}` and `{Bibliography}` become citations and the reference list, at the place of the `::: {#refs}` block or at the end. On macOS an agent can run Refresh: `osascript -e 'tell application "Microsoft Word" to run VB macro macro name "ZoteroRefresh"'`. The document must be open and in front. The command returns before Zotero has finished: wait until the citations have changed, then save the file and run `check`. A file saved too early still shows the old style.
- To change the style later, use Document Preferences in the Zotero tab, or run `prefs` again and refresh.

## EndNote

Needs EndNote with Cite While You Write in Word, and the library that Word will use.

```bash
python3 scripts/live_citations.py endnote ms.md --library library.xml --bibliography refs.json -o ms.endnote.md
pandoc ms.endnote.md -o ms.docx
```

- `library.xml` is that library exported as EndNote XML (File > Export, XML). The script writes temporary citations with each record's number: `{Okafor, 2021 #12}`, or `{Okafor, 2021 #12;Lindqvist, 2019 #4}` for several.
- Record numbers belong to one library. A copy, a synced library on another computer or a colleague's library numbers its records differently, so export from the library that will be open in Word.
- Open the file in Word with that library open and click Update Citations and Bibliography in the EndNote tab. Cite While You Write has no macro or menu command for this, so the researcher clicks it once, or an agent with screen control does. Screen control reaches the button only when the Word window is on the current desktop. EndNote puts the reference list at the end of the document.

## Checks after the refresh

```bash
python3 scripts/live_citations.py check ms.docx
```

- It counts the citation and bibliography fields and lists what is left: placeholders not refreshed, temporary citations not updated (or with no record in the open library), pandoc keys left as text, and both managers in one file. It exits 0 only when every citation is a live field.
- Compare the number of citation fields with the number of citation groups that the conversion reported.
- Read the reference list once against the bibliography, and check numbered references for order and gaps (`check_references.py refs.ris --manuscript ms.docx`).

## Trying a new setup

- Test on a test document, never on the manuscript.
- Zotero: use a test collection in the researcher's library. A second library needs a second Zotero profile with the plugins installed again. Items imported through the connector land in the collection selected in Zotero, and a synced library sends test items to zotero.org; delete them afterwards, through the trash, after asking.
- EndNote: make a test library, for example from the sample library that EndNote installs.
- Agents need permission to reach Zotero's local port and to run `osascript` outside their sandbox. Ask the researcher first.
- Prefer each program's own interfaces (the local port, AppleScript, Word macros) to screen control.
- Tested on macOS with Zotero 10, Better BibTeX 9, EndNote 2025 and Word for Mac. Not tested on Windows, where Refresh and Update are clicked in the Word ribbon.

## Field formats

For agents that write fields without the script:

- Zotero citation: `ADDIN ZOTERO_ITEM CSL_CITATION {json}`. The JSON holds `citationID`, `properties` (`formattedCitation`, `plainCitation`, `noteIndex`: 0), `citationItems` and `schema`. Each item has `id` and `uris` set to the item's URI and `itemData` in CSL JSON. Item URIs are `http://zotero.org/users/<user ID>/items/<item key>`, or `http://zotero.org/users/local/<ID>/items/<item key>` for a library that is not synced.
- Zotero bibliography: `ADDIN ZOTERO_BIBL {"uncited":[],"omitted":[],"custom":[]} CSL_BIBLIOGRAPHY`.
- Zotero document preferences: custom document properties `ZOTERO_PREF_1`, `ZOTERO_PREF_2` and so on, each at most 255 characters, holding `<data data-version="3" zotero-version="…"><session id="…"/><style id="http://www.zotero.org/styles/<style>" hasBibliography="1" bibliographyStyleHasBeenSet="0"/><prefs><pref name="fieldType" value="Field"/></prefs></data>`.
- In pandoc Markdown a field is a raw OpenXML inline, `` `<w:r>…</w:r>`{=openxml} ``, with the field's begin, instruction, separator, shown text and end runs. A backtick inside the JSON is written ```.
- EndNote temporary citation: `{First author's surname, Year #Record number}`, several joined by `;`, with the braces escaped (`\{ \}`) in pandoc Markdown. After the update the fields are `ADDIN EN.CITE` and `ADDIN EN.REFLIST`.
