---
name: amazon-3c-compliance-risk
description: Screens Amazon 3C product ideas for compliance, IP, battery, wireless, electrical, charger, safety, and after-sales risk before product selection. Use when evaluating regulated 3C items, batteries, chargers, Bluetooth/Wi-Fi, FCC, UL, patent, warranty, or product liability risk.
---

# 3C Compliance Risk

## Hard Rule

This skill is a risk screen, not legal advice. Verify current Amazon Seller Central, US/EU regulations, supplier certificates, and counsel before sourcing or listing.

## Risk Buckets

1. Battery: lithium battery, power bank, rechargeable device, coin/button cell.
2. Wireless/RF: Bluetooth, Wi-Fi, cellular, remote control, transmitter/receiver.
3. Electrical safety: charger, adapter, AC plug, fast charging, heat generation.
4. Consumer safety: child-facing electronics, wearable electronics, skin contact.
5. IP/design: patents, trade dress, brand compatibility claims, MFi-like claims.
6. Platform enforcement: gated categories, hazmat, documentation mismatch, recall risk.
7. Operational load: warranty, defect rate, replacement cost, firmware/app support.

## Workflow

1. Mark each candidate as `green`, `yellow`, or `red` for every bucket.
2. Require document evidence for yellow/red: test report, certificate, SDS, UN38.3, FCC ID/SDoC, safety standard, supplier authorization, patent search note.
3. For 3C accessories, prefer passive or low-risk products first: stands, holders, organizers, mounts, sleeves, covers, adapters without active electronics.
4. Treat claims as risk: "for Apple", "MagSafe", "MFi", "fast charge", "UL certified", "kid-safe", "medical grade".
5. Reject until proven otherwise if the product needs active certification but the supplier cannot provide matching model-level documents.

## Output Fields

`candidate`, `batteryRisk`, `wirelessRisk`, `electricalRisk`, `childRisk`, `ipRisk`, `hazmatRisk`, `documentEvidence`, `riskClass`, `mustVerifyBeforeOrder`.
