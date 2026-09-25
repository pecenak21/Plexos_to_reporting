## EPIC H — Reporting: the build report and the diff report

**Component C8.** Phase 7. **Q11 splits this into two artifacts, and the technical design's §11 ("one combined artifact") is now out of date.** APS's answer: *"the build report can be flat. The diff report should be a workbook. There should be a summary page, then detailed pages."*

| Artifact | Answers | Form | Produced by |
|---|---|---|---|
| **Build report** | *What did the build decide, and what should I check?* | **Flat** — one plain-text `.txt` file | Every build, including a failed one |
| **Diff report** | *What changed since last time?* | **Workbook** — a summary page then detail pages | Every build with a baseline, and every standalone comparison |

The split is not just formatting. The build report is the home of §2.1's rule — **anything the diff cannot catch must be said in words** — and that content has no natural place in a diff workbook, because by definition it is what the diff does not show. Keeping them separate stops the one thing the comparison structurally cannot tell you from being filed behind five sheets of things it can.

`APS_Build_Report_Example.xlsx` remains the shape reference for the **diff** report. The build report is new and has no mock-up yet.
