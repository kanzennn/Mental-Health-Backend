from app.models.user_model import User


class UserRepository:

    def create(self, db, name: str, email: str, password_hash: str) -> User:
        user = User(name=name, email=email, password=password_hash)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_all(self, db) -> list[User]:
        return db.query(User).all()

    def get_by_id(self, db, user_id) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def find_by_email(self, db, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def update(self, db, user_id, **kwargs) -> User | None:
        user = self.get_by_id(db, user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
