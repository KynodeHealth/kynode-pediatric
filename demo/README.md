# KYNODE Pediatric Demo

Generate the synthetic demo payload from the standalone packages:

```bash
python3 demo/generate_demo_data.py
python3 -m http.server 8080 -d demo
```

Open `http://localhost:8080`.

The demo is English-first with Spanish support. It uses synthetic data only and demonstrates point-of-care support plus aggregated climate-health signal generation. It is not a production UI.
