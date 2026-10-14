import pytest
from app import create_app,db

@pytest.fixture()
def client():
    app=create_app({"TESTING":True,"SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:"})
    with app.test_client() as c: yield c
    with app.app_context(): db.drop_all()

def test_rooms_and_health(client):
    assert client.get("/healthz").status_code==200
    assert len(client.get("/api/rooms").get_json())==3

def test_booking_and_overlap(client):
    payload={"room_id":1,"guest_name":"Suhana","email":"test@example.com","guests":2,
             "check_in":"2026-11-10","check_out":"2026-11-12"}
    assert client.post("/api/reservations",json=payload).status_code==201
    assert client.post("/api/reservations",json=payload).status_code==409

def test_availability_excludes_booking(client):
    payload={"room_id":1,"guest_name":"Suhana","email":"test@example.com","guests":2,
             "check_in":"2026-11-10","check_out":"2026-11-12"}
    client.post("/api/reservations",json=payload)
    result=client.get("/api/availability?check_in=2026-11-10&check_out=2026-11-12&guests=2").get_json()
    assert 1 not in [r["id"] for r in result]

def test_review_validation(client):
    assert client.post("/api/reviews",json={"guest_name":"A","rating":5,"comment":"Great"}).status_code==201
    assert client.post("/api/reviews",json={"guest_name":"A","rating":7,"comment":"No"}).status_code==400
