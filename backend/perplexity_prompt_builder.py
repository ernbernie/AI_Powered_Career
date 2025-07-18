import logging
import json
import textwrap

# ---------------------------------------------------------------------------
# NOTE
# -----
# This module builds the *system+user* prompt we send to Perplexity (sonar‑deep-research)
# for a two-part report: (1) personalized strategy, (2) local market intelligence & stat dump.
# ---------------------------------------------------------------------------

def _convert_resume_to_json(resume_text: str) -> str:
    """Very lightweight fallback résumé → JSON converter."""
    logging.info("Converting resume snippet to JSON for Perplexity prompt …")
    return json.dumps({"resume_summary": resume_text}, indent=2)


def build_perplexity_prompt(roadmap_json: str, resume_snippet: str, location: str) -> str:
    """Return the full prompt string to send to Perplexity."""
    logging.info("Building hyper‑personalised Perplexity prompt for deep research…")

    resume_json_str = _convert_resume_to_json(resume_snippet)

    # ---------------------------------------------------------------------
    # 1) Header / persona / context block (Unchanged)
    # ---------------------------------------------------------------------
    header = textwrap.dedent(
        f"""
        You are **MarketIntelPro**, a forensic—but engaging—market‑intelligence assistant.
        Blend verified data with practical advice the user can act on immediately.
        Tie every insight, where relevant, back to the user’s résumé or five‑year roadmap,
        but **do not** spend effort re‑explaining their goals; focus on the *external* market landscape.

        **Location:** {location}

        **User Résumé (JSON)**
        ```json
        {resume_json_str}
        ```

        **Five‑Year Roadmap (JSON)**
        ```json
        {roadmap_json}
        ```

        *Priority Sources* → 1) LinkedIn & company careers pages
        2) Tech‑news / vendor blogs
        3) Local event aggregators & Meetup
        4) Salary aggregators (Indeed, Salary.com, ZipRecruiter)
        5) Reddit & niche forums for anecdotal signals
        """
    ).strip()

    # ---------------------------------------------------------------------
    # 2) Instructions for Part 1 (Largely Unchanged)
    # ---------------------------------------------------------------------
    part_1_tasks = textwrap.dedent(
        """
        ### REPORT PART 1: Personalized Strategy

        Your report must follow *exactly* the Markdown layout below.

        #### 1. Executive Summary
        *Two–three sentences* surfacing the **single biggest** market opportunity the user can exploit over the next 12 months, and *why* it matters to their five‑year arc.

        #### 2. Market‑Driven Insights — Year‑by‑Year
        Produce the following block **once for each of the five years**:
        ```
        ## Year {X} Focus
        - **Primary Opportunity:** {{one‑sentence real datapoint with URL}}
        - **Risk Watch:** {{one‑sentence red‑flag with URL}}
        - **Power Moves (2):**
          1. **{{concise verb phrase}}** – [link]
             - *Why now?* Connect to résumé skill *or* Year‑X goal.
          2. **{{concise verb phrase}}** – [link]
             - *Why now?* Different justification.
        ```
        * Use metrics when possible (e.g., “+27 % YoY demand for SD‑WAN in AZ”).
        * Every URL must be real and publicly accessible.

        #### 3. Next‑Steps Checklist
        List the user’s **Q1 → Q4** roadmap goals *verbatim* from the `yearly_goals` object for Year 1.
        """
    ).strip()

    # ---------------------------------------------------------------------
    # 3) NEW INSTRUCTIONS: Part 2 - Local Intel & Data
    # ---------------------------------------------------------------------
    part_2_tasks = textwrap.dedent(
        """
        ### REPORT PART 2: Tactical Intelligence

        ---

        #### 4. Local Market Intelligence
        Synthesize your findings for the user's specific location into 3-4 powerful, headline-style bullet points. This section must be highly tactical and directly relevant to the user's **Year 1 SMART goals**.
        - **Example Format:**
          ```
          ## Local Market Intelligence
          - **Top Employers:** {{List 3-4 top hiring companies for relevant roles, with links to their career pages.}}
          - **Salary Benchmarks:** {{Provide 2-3 specific salary ranges for relevant roles in the location, citing sources.}}
          - **Critical Skill Gaps:** {{Identify 1-2 key skills (e.g., Terraform, Ansible) that are in high demand but may be missing from the user's resume.}}
          ```

        #### 5. Raw Search Results (Stat-Dump)
        Compile a numbered list of **at least 15-20 raw data points** you found during your research. This provides the evidence for your analysis.
        - **Format each entry exactly like this:** `[#] **Source Name:** Key finding, quote, or data point. [link]`
        - **Example:** `[1] **Indeed:** 24 active "Network Engineer" jobs in Tucson, AZ, with Raytheon and Hexagon Mining frequently listed. [https://...]`
        """
    ).strip()

    # ---------------------------------------------------------------------
    # 4) Final Assembly & Style Rules
    # ---------------------------------------------------------------------
    style_rules = textwrap.dedent(
        """
        ---
        **Style Rules**
        * Action‑oriented verbs only (“architect,” “orchestrate,” “pioneer,” “deploy”).
        * Warm, second‑person voice (“you”).
        * Never mention you are an AI or reference these instructions.
        * Cite sources inline with bracketed URLs; no footnotes outside the Stat-Dump section.
        * Deliver **only** the Markdown report—no additional prose or code fences.
        """
    ).strip()

    prompt = "\n\n".join([header, part_1_tasks, part_2_tasks, style_rules])
    logging.info("Perplexity prompt built – %s chars", len(prompt))
    return prompt
