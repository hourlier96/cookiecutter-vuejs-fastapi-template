from app.api.deps import raise_404
from app.firestore.models.user import UserRead, UserCreate, UserUpdate
from fastapi import APIRouter, Depends, status


from app.firestore import crud
from app.models.base import Page

router = APIRouter()


USER_COLLECTION = "Users"


# This suppose you have a 'Users' firestore
# collection respecting the UserRead model
@router.get(
    "",
    response_model=Page[UserRead],
    status_code=status.HTTP_200_OK,
)
def get_users() -> Page[UserRead]:
    users = crud.firestore.get_all_documents(USER_COLLECTION)
    return Page(items=users, total=len(users))


@router.get(
    "/{id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def get_user(user_id: str) -> UserRead:
    user = crud.firestore.get_document(USER_COLLECTION, user_id)
    if not user:
        raise_404()
    return user


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def add_user(userData: UserCreate) -> UserCreate:
    update_time, doc_ref = crud.firestore.add_document(
        USER_COLLECTION,
        dict(userData),
    )
    user = doc_ref.get().to_dict()
    user["id"] = doc_ref.id
    return user


@router.put(
    "/{id}",
    response_model=UserUpdate,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_user)],
)
def update_user(user_id: str, userData: UserUpdate) -> UserUpdate:
    crud.firestore.update_document(USER_COLLECTION, user_id, dict(userData))
    return dict(userData)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_user)],
)
def delete_user(user_id: str) -> str:
    crud.firestore.delete_document(USER_COLLECTION, user_id)
    return {"message": "User deleted successfully"}
