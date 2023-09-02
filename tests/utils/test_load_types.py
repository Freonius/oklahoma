# from pytest import raises
# from fastapi.routing import APIRouter


# def test_load_instances():
#     from oklahoma.utils import load_types

#     routers = load_types(
#         APIRouter,
#         instance=True,
#         cwd=None,
#         folder_name="tests/src",
#     )
#     assert len(routers) == 2
#     assert all(isinstance(x, APIRouter) for x in routers)
#     assert all(x.prefix.startswith("/api/t1") for x in routers)


# def test_load_types_fails():
#     from oklahoma.utils import load_types
#     from oklahoma.exceptions import ModuleLoadingError

#     with raises(ModuleLoadingError):
#         load_types(APIRouter, folder_name="tests/not")


# def test_load_classes():
#     from oklahoma.db import Base
#     from oklahoma.utils import load_types

#     bases = load_types(
#         Base,
#         instance=False,
#         cwd=None,
#         folder_name="tests/src",
#     )

#     assert len(bases) == 2
#     assert all(issubclass(x, Base) for x in bases)
#     assert all(x.__tablename__ in ("firsts", "seconds") for x in bases)
