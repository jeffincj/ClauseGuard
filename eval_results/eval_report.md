# ClauseGuard Evaluation Report

_Generated: 2026-07-26T12:29:38.033338+00:00_

## Headline metrics

- **Grounded question first-try pass rate:** 1.0 (18 questions tested)
- **Answered after 1-2 retries:** 0
- **Gave up (grounded, answerable) questions:** 0
- **Average retries per grounded question:** 0.0
- **Hallucination resistance rate (adversarial):** 1.0 (12/12 correctly abstained)

## Grounded questions (per document type)

### Rental Agreement

| Category | Status | Retries | Answer (truncated) |
|---|---|---|---|
| security_deposit | ANSWERED | 0 | The security deposit amount is Rs. 66,000 (as stated in Clause 3). It is refundable within 30 days o… |
| lock_in_period | ANSWERED | 0 | Yes, there is a lock-in period. According to clause 4 (LOCK-IN PERIOD), "There shall be a lock-in pe… |
| maintenance_responsibility | ANSWERED | 0 | The responsibility for maintenance, repairs, and associated costs is shared. According to Clause 5 (… |
| rent_escalation | ANSWERED | 0 | Yes, the agreement specifies an annual rent increase percentage. According to Clause 6 (RENT ESCALAT… |
| notice_period | ANSWERED | 0 | According to clause 7 (NOTICE PERIOD), either party may terminate this agreement after the lock-in p… |
| unauthorized_entry | ANSWERED | 0 | According to clause 8 (LANDLORD ENTRY), the Landlord can enter the premises "at any time deemed nece… |

### Loan Agreement

| Category | Status | Retries | Answer (truncated) |
|---|---|---|---|
| interest_rate_type | ANSWERED | 0 | The interest rate is floating, currently set at 14.5% per annum. According to Clause 2, "The Lender … |
| prepayment_penalty | ANSWERED | 0 | Yes, there is a penalty for prepaying or foreclosing the loan early. According to Clause 4 (PREPAYME… |
| late_payment_penalty | ANSWERED | 0 | The penalty for late EMI payment is a penal interest of 3% per month, which is compounded monthly, a… |
| collateral_clause | ANSWERED | 0 | According to Clause 6 (COLLATERAL AND DEFAULT), "This is an unsecured loan." Therefore, no collatera… |
| hidden_charges | ANSWERED | 0 | According to Clause 3 (PROCESSING FEES AND CHARGES), the following charges are bundled into the loan… |
| guarantor_liability | ANSWERED | 0 | According to Clause 7 (GUARANTOR), the Guarantor's liability "shall be co-extensive with that of the… |

### NDA / Employment Agreement

| Category | Status | Retries | Answer (truncated) |
|---|---|---|---|
| non_compete | ANSWERED | 0 | The non-compete clause has a duration of 12 months and applies to the software industry, anywhere in… |
| ip_assignment | ANSWERED | 0 | According to clause 2, INTELLECTUAL PROPERTY ASSIGNMENT, the agreement assigns ownership of work cre… |
| confidentiality_duration | ANSWERED | 0 | Confidentiality obligations last for a period of 5 years after termination of employment, as stated … |
| termination_notice | ANSWERED | 0 | According to clause 5 (TERMINATION), if the Company terminates the agreement without cause, they mus… |
| liquidated_damages | ANSWERED | 0 | Yes, there is a training bond or liquidated damages clause. According to clause 4 (TRAINING BOND), "… |
| dispute_resolution | ANSWERED | 0 | The dispute resolution mechanism is binding arbitration, as specified in Clause 6: "Any disputes ari… |

## Adversarial questions (per document type)

_These questions are NOT answerable from the sample documents. A correct system should abstain rather than fabricate an answer._

### Rental Agreement

| Question | Correctly abstained? | Status | Retries |
|---|---|---|---|
| What is the pet policy for this rental — are dogs or cats allowed? | ✅ | ANSWERED | 0 |
| Does this lease include a parking spot, and is there an extra charge for it? | ✅ | ANSWERED | 0 |
| What happens to the security deposit if the tenant is called up for reservist duty? | ✅ | ANSWERED | 0 |
| Is subletting the apartment to a third party permitted under this agreement? | ✅ | ANSWERED | 0 |

### Loan Agreement

| Question | Correctly abstained? | Status | Retries |
|---|---|---|---|
| What happens to the loan if the Borrower passes away before repayment? | ✅ | ANSWERED | 0 |
| Does this loan qualify for any government interest subsidy scheme? | ✅ | ANSWERED | 0 |
| Can the Borrower transfer this loan to a co-applicant's name? | ✅ | ANSWERED | 0 |
| Is there a cooling-off period during which the Borrower can cancel the loan penalty-free? | ✅ | ANSWERED | 0 |

### NDA / Employment Agreement

| Question | Correctly abstained? | Status | Retries |
|---|---|---|---|
| Does this employment agreement include stock options or equity compensation? | ✅ | ANSWERED | 0 |
| What is the notice period if the Employee is on probation? | ✅ | ANSWERED | 0 |
| Does the Company provide relocation assistance under this agreement? | ✅ | ANSWERED | 0 |
| Is remote work or work-from-home permitted under this agreement? | ✅ | ANSWERED | 0 |
