"""
Adversarial questions deliberately NOT answerable from the three sample
documents in data/sample_docs/. These test whether ClauseGuard correctly
admits "I can't verify this" (GAVE_UP after retries) rather than
hallucinating a plausible-sounding but fabricated answer.

This is the key number for a placement portfolio: a RAG system's realistic
failure mode isn't "gets grounded questions wrong" — it's "confidently
answers things the document never said." These questions specifically
probe that failure mode.
"""

RENTAL_ADVERSARIAL = [
    "What is the pet policy for this rental — are dogs or cats allowed?",
    "Does this lease include a parking spot, and is there an extra charge for it?",
    "What happens to the security deposit if the tenant is called up for reservist duty?",
    "Is subletting the apartment to a third party permitted under this agreement?",
]

LOAN_ADVERSARIAL = [
    "What happens to the loan if the Borrower passes away before repayment?",
    "Does this loan qualify for any government interest subsidy scheme?",
    "Can the Borrower transfer this loan to a co-applicant's name?",
    "Is there a cooling-off period during which the Borrower can cancel the loan penalty-free?",
]

NDA_EMPLOYMENT_ADVERSARIAL = [
    "Does this employment agreement include stock options or equity compensation?",
    "What is the notice period if the Employee is on probation?",
    "Does the Company provide relocation assistance under this agreement?",
    "Is remote work or work-from-home permitted under this agreement?",
]

ADVERSARIAL_QUESTIONS = {
    "rental": RENTAL_ADVERSARIAL,
    "loan": LOAN_ADVERSARIAL,
    "nda_employment": NDA_EMPLOYMENT_ADVERSARIAL,
}
