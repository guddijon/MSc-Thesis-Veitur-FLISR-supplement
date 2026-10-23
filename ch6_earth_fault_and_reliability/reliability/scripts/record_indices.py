"""Measured reliability indices of the Akranes 11 kV network faults, January 2020 to October 2026 (thesis Section 6.4,
subsection on the measured fault record).

Inputs: data/akranes_11kv_events_2020-2026.csv (one row per unplanned event; customers and customer-minutes counted
per station from the outage reports with the customer register) and data/customers_per_station.csv (3 516 customers
in 47 stations). The 11 kV network faults are the cable faults and the station-equipment fault; the overload trips,
the customer-installation faults, the mis-operation and the 66 kV events are listed but not counted.
Output: output/record_indices.csv (one row per quantity).
Run: python3 record_indices.py"""
import csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEARS = 6.83                                                     # January 2020 to October 2026
FAULT_CLASSES = ('11kV cable fault', '11kV cable fault (x2)', '11kV equipment fault')

events = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'akranes_11kv_events_2020-2026.csv'))))
customers = sum(int(r['customers']) for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'customers_per_station.csv'))))
faults = [r for r in events if r['event_class'] in FAULT_CLASSES]
ci = sum(int(r['customers_interrupted']) for r in faults)
cm = sum(int(r['customer_minutes']) for r in faults)
largest = max(faults, key=lambda r: int(r['customer_minutes']))
cm_largest = int(largest['customer_minutes'])
rows = [('events', len(faults)), ('register_customers', customers), ('years', YEARS),
        ('customers_interrupted', ci), ('customer_minutes', cm),
        ('saifi_per_year', round(ci / customers / YEARS, 4)), ('saidi_min_per_year', round(cm / customers / YEARS, 2)),
        ('customer_minutes_per_customer', round(cm / customers, 1)),
        ('largest_event_date', largest['date']), ('largest_event_customers', int(largest['customers_interrupted'])),
        ('largest_event_customer_minutes_per_customer', round(cm_largest / customers, 1)),
        ('largest_event_saidi_min_per_year', round(cm_largest / customers / YEARS, 2)),
        ('saidi_without_largest_min_per_year', round((cm - cm_largest) / customers / YEARS, 2))]
os.makedirs(os.path.join(ROOT, 'output'), exist_ok=True)
with open(os.path.join(ROOT, 'output', 'record_indices.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['quantity', 'value']); w.writerows(rows)
for k, v in rows: print(f'{k:46s} {v}')
