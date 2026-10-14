from datetime import date, datetime
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    guest_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500), nullable=False)

def room_dict(room):
    return {"id":room.id,"name":room.name,"description":room.description,
            "price":room.price,"capacity":room.capacity}

def create_app(config=None):
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///hotel.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
    if config: app.config.update(config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if Room.query.count()==0:
            db.session.add_all([
                Room(name="Garden King",description="King room overlooking the garden.",price=189,capacity=2),
                Room(name="Courtyard Suite",description="Spacious suite with a private sitting area.",price=259,capacity=3),
                Room(name="Family Loft",description="Flexible loft for families and small groups.",price=319,capacity=4),
            ])
            db.session.commit()

    @app.get("/")
    def home(): return render_template("index.html")

    @app.get("/healthz")
    def health(): return jsonify(status="healthy")

    @app.get("/api/rooms")
    def rooms(): return jsonify([room_dict(r) for r in Room.query.order_by(Room.price).all()])

    @app.get("/api/availability")
    def availability():
        try:
            start=date.fromisoformat(request.args["check_in"])
            end=date.fromisoformat(request.args["check_out"])
            guests=int(request.args.get("guests",1))
        except (KeyError,ValueError):
            return jsonify(error="valid check_in, check_out and guests are required"),400
        if end<=start or guests<1: return jsonify(error="invalid stay dates or guest count"),400
        booked={r.room_id for r in Reservation.query.filter(
            Reservation.check_in < end, Reservation.check_out > start).all()}
        available=Room.query.filter(Room.capacity>=guests).all()
        return jsonify([room_dict(r) for r in available if r.id not in booked])

    @app.post("/api/reservations")
    def reserve():
        data=request.get_json(silent=True) or {}
        try:
            room_id=int(data["room_id"]); guests=int(data["guests"])
            start=date.fromisoformat(data["check_in"]); end=date.fromisoformat(data["check_out"])
            name=str(data["guest_name"]).strip(); email=str(data["email"]).strip()
        except (KeyError,ValueError,TypeError):
            return jsonify(error="missing or invalid reservation fields"),400
        room=db.session.get(Room,room_id)
        if not room or not name or "@" not in email or guests<1 or guests>room.capacity or end<=start:
            return jsonify(error="reservation details are invalid"),400
        overlap=Reservation.query.filter(Reservation.room_id==room_id,
            Reservation.check_in<end,Reservation.check_out>start).first()
        if overlap: return jsonify(error="room is not available for those dates"),409
        item=Reservation(room_id=room_id,guest_name=name,email=email,guests=guests,
                         check_in=start,check_out=end)
        db.session.add(item); db.session.commit()
        return jsonify(id=item.id,status="confirmed",room=room.name),201

    @app.get("/api/reviews")
    def reviews():
        return jsonify([{"id":r.id,"guest_name":r.guest_name,"rating":r.rating,"comment":r.comment}
                        for r in Review.query.order_by(Review.id.desc()).limit(20)])

    @app.post("/api/reviews")
    def add_review():
        data=request.get_json(silent=True) or {}
        try: rating=int(data["rating"])
        except (KeyError,ValueError,TypeError): return jsonify(error="rating must be 1-5"),400
        name=str(data.get("guest_name","")).strip(); comment=str(data.get("comment","")).strip()
        if not name or not comment or rating not in range(1,6):
            return jsonify(error="name, comment and rating 1-5 are required"),400
        review=Review(guest_name=name,rating=rating,comment=comment)
        db.session.add(review); db.session.commit()
        return jsonify(id=review.id),201
    return app

app=create_app()
if __name__=="__main__": app.run(debug=True)
