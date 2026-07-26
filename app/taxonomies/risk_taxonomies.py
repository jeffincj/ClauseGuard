"""
Domain knowledge: for each document type, a list of clause categories
ClauseGuard scans for. Each category has:
  - key: internal id
  - label: human-readable name
  - probe_question: what we ask the RAG pipeline to find/assess this clause
  - why_it_matters: shown to the user alongside the verdict

This taxonomy is what makes ClauseGuard more than "summarize my PDF" —
it's a structured, domain-aware risk scan.
"""

RENTAL_AGREEMENT = [
    {
        "key": "security_deposit",
        "label": "Security Deposit Terms",
        "probe_question": "What is the security deposit amount, and under what conditions is it refundable or forfeited?",
        "why_it_matters": "Unclear deposit-return conditions are a top source of landlord-tenant disputes.",
    },
    {
        "key": "lock_in_period",
        "label": "Lock-in Period / Early Termination Penalty",
        "probe_question": "Is there a lock-in period, and what penalty applies if the tenant leaves early?",
        "why_it_matters": "Lock-in clauses can trap tenants into paying rent for months they don't occupy.",
    },
    {
        "key": "maintenance_responsibility",
        "label": "Maintenance & Repair Responsibility",
        "probe_question": "Who is responsible for maintenance, repairs, and associated costs — landlord or tenant?",
        "why_it_matters": "Ambiguous maintenance clauses shift unexpected costs onto tenants.",
    },
    {
        "key": "rent_escalation",
        "label": "Rent Escalation Clause",
        "probe_question": "Does the agreement specify an annual rent increase percentage, and how is it applied?",
        "why_it_matters": "Uncapped or steep escalation clauses can make renewals unaffordable.",
    },
    {
        "key": "notice_period",
        "label": "Notice Period for Termination",
        "probe_question": "What notice period is required from either party to terminate the agreement?",
        "why_it_matters": "Short or one-sided notice periods disadvantage the tenant.",
    },
    {
        "key": "unauthorized_entry",
        "label": "Landlord Entry Rights",
        "probe_question": "Under what conditions and with what notice can the landlord enter the property?",
        "why_it_matters": "Vague entry rights can compromise tenant privacy.",
    },
]

LOAN_AGREEMENT = [
    {
        "key": "interest_rate_type",
        "label": "Interest Rate Type & Reset Terms",
        "probe_question": "Is the interest rate fixed or floating, and under what conditions can it be reset?",
        "why_it_matters": "Floating rates with vague reset terms can cause unpredictable EMI jumps.",
    },
    {
        "key": "prepayment_penalty",
        "label": "Prepayment / Foreclosure Penalty",
        "probe_question": "Is there a penalty for prepaying or foreclosing the loan early, and how much?",
        "why_it_matters": "High prepayment penalties trap borrowers who want to exit debt early.",
    },
    {
        "key": "late_payment_penalty",
        "label": "Late Payment Penalty & Compounding",
        "probe_question": "What is the penalty for late EMI payment, and is it compounded?",
        "why_it_matters": "Compounding late fees can spiral small missed payments into large debts.",
    },
    {
        "key": "collateral_clause",
        "label": "Collateral / Default Recovery Terms",
        "probe_question": "What collateral is pledged, and what happens to it in case of default?",
        "why_it_matters": "Borrowers often don't realize how quickly collateral can be seized on default.",
    },
    {
        "key": "hidden_charges",
        "label": "Processing Fees & Hidden Charges",
        "probe_question": "What processing fees, insurance add-ons, or other charges are bundled into the loan?",
        "why_it_matters": "Bundled charges inflate the effective interest rate beyond the stated rate.",
    },
    {
        "key": "guarantor_liability",
        "label": "Guarantor Liability Scope",
        "probe_question": "If there is a guarantor, what is the extent of their liability on default?",
        "why_it_matters": "Guarantors often unknowingly accept unlimited liability.",
    },
]

NDA_EMPLOYMENT_AGREEMENT = [
    {
        "key": "non_compete",
        "label": "Non-Compete Scope & Duration",
        "probe_question": "What is the duration and geographic/industry scope of any non-compete clause?",
        "why_it_matters": "Overly broad non-competes can be unenforceable but still deter employees from switching jobs.",
    },
    {
        "key": "ip_assignment",
        "label": "IP Assignment Scope",
        "probe_question": "Does the agreement assign ownership of work created outside work hours or unrelated to the employer's business?",
        "why_it_matters": "Overreaching IP clauses can claim ownership of personal side projects.",
    },
    {
        "key": "confidentiality_duration",
        "label": "Confidentiality Duration",
        "probe_question": "How long do confidentiality obligations last after employment ends?",
        "why_it_matters": "Indefinite confidentiality terms can be overly restrictive long after leaving.",
    },
    {
        "key": "termination_notice",
        "label": "Termination Notice & Severance",
        "probe_question": "What notice period or severance applies if the employer terminates without cause?",
        "why_it_matters": "One-sided termination terms leave employees with little financial cushion.",
    },
    {
        "key": "liquidated_damages",
        "label": "Liquidated Damages / Bond Clause",
        "probe_question": "Is there a training bond or liquidated damages clause if the employee resigns early?",
        "why_it_matters": "Bond clauses can lock employees into jobs under threat of a large payout.",
    },
    {
        "key": "dispute_resolution",
        "label": "Dispute Resolution & Jurisdiction",
        "probe_question": "What is the dispute resolution mechanism (arbitration/court) and jurisdiction specified?",
        "why_it_matters": "Distant or employer-favorable jurisdictions make disputes costly for employees to pursue.",
    },
]

TAXONOMIES = {
    "rental": RENTAL_AGREEMENT,
    "loan": LOAN_AGREEMENT,
    "nda_employment": NDA_EMPLOYMENT_AGREEMENT,
}

DOC_TYPE_LABELS = {
    "rental": "Rental Agreement",
    "loan": "Loan Agreement",
    "nda_employment": "NDA / Employment Agreement",
}
