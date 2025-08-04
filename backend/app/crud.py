# crud.py
def create_truck(db: Session, truck: schemas.TruckCreate):
    try:
        db_truck = models.Truck(**truck.dict())
        db.add(db_truck)
        db.commit()
        db.refresh(db_truck)
        return db_truck
    except Exception as e:
        print("❌ Error in create_truck:", e)
        raise
