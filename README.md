# Boutique Hotel Booking Platform

A reconstructed full-stack version of the Hotel Website described on Suhana Patel's resume. The original source files were unavailable, so this repository implements the stated scope: responsive Bootstrap/JavaScript UI, room discovery, booking/reservation management, interactive gallery, and guest reviews.

## Features

- Responsive Bootstrap interface
- Room cards with nightly rates and capacity
- Date/guest availability search
- Reservation creation with server-side validation
- Overlap checks to prevent double-booking a room
- SQLite persistence through SQLAlchemy
- Interactive image gallery
- Guest review submission and display
- REST API for rooms, availability, reservations, and reviews
- Docker support and automated tests

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000.

## API

- `GET /api/rooms`
- `GET /api/availability?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&guests=2`
- `POST /api/reservations`
- `GET /api/reviews`
- `POST /api/reviews`
- `GET /healthz`

## Portfolio note

The original resume stated that the website increased direct reservations by one-third. No analytics or original deployment evidence was supplied, so this reconstructed repository **does not repeat or claim that metric**.

This implementation is suitable for demonstrating frontend, API, database, validation, and containerization skills.
