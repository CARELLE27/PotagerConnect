"""Forum d'entraide et troc - US-15 / US-16 / US-17 (COULD).

Poster une demande d'aide ou une annonce de troc, commenter les posts des autres.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import CommentaireForum, PostForum, TypePostEnum, User
from app.schemas import (
    CommentaireCreate,
    CommentaireOut,
    PostCreate,
    PostDetail,
    PostOut,
)

router = APIRouter(prefix="/forum", tags=["forum"])


def _post_to_out(post: PostForum) -> PostOut:
    return PostOut(
        id=post.id,
        user_id=post.user_id,
        auteur_nom=post.auteur.nom_complet if post.auteur else None,
        titre=post.titre,
        contenu=post.contenu,
        type=post.type.value,
        created_at=post.created_at,
        nb_commentaires=len(post.commentaires),
    )


def _comm_to_out(c: CommentaireForum) -> CommentaireOut:
    return CommentaireOut(
        id=c.id,
        post_id=c.post_id,
        user_id=c.user_id,
        auteur_nom=c.auteur.nom_complet if c.auteur else None,
        contenu=c.contenu,
        created_at=c.created_at,
    )


@router.get("", response_model=list[PostOut])
def liste_posts(
    type: str | None = Query(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste des posts, filtrable par type (entraide / troc)."""
    query = db.query(PostForum)
    if type in ("entraide", "troc"):
        query = query.filter(PostForum.type == type)
    posts = query.order_by(PostForum.created_at.desc()).all()
    return [_post_to_out(p) for p in posts]


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def creer_post(
    payload: PostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """US-15 / US-17 : poster une demande d'entraide ou une annonce de troc."""
    type_post = TypePostEnum.troc if payload.type == "troc" else TypePostEnum.entraide
    post = PostForum(
        user_id=user.id,
        titre=payload.titre.strip(),
        contenu=payload.contenu.strip(),
        type=type_post,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return _post_to_out(post)


@router.get("/{post_id}", response_model=PostDetail)
def detail_post(
    post_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    post = db.get(PostForum, post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post introuvable")
    base = _post_to_out(post)
    return PostDetail(
        **base.model_dump(),
        commentaires=[_comm_to_out(c) for c in post.commentaires],
    )


@router.post(
    "/{post_id}/commentaires",
    response_model=CommentaireOut,
    status_code=status.HTTP_201_CREATED,
)
def commenter(
    post_id: int,
    payload: CommentaireCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """US-16 : commenter un post pour aider un autre jardinier."""
    post = db.get(PostForum, post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post introuvable")

    commentaire = CommentaireForum(
        post_id=post.id, user_id=user.id, contenu=payload.contenu.strip()
    )
    db.add(commentaire)
    db.commit()
    db.refresh(commentaire)
    return _comm_to_out(commentaire)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_post(
    post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """L'auteur peut supprimer son propre post."""
    post = db.get(PostForum, post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post introuvable")
    if post.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ce n'est pas votre post")
    db.delete(post)
    db.commit()
