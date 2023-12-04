from hypothesis import given
from hypothesis import strategies as st
from main import Cursor, Direction, Vector


class TestCursor:
    def test_rotate(self):
        cursor = Cursor()
        assert cursor.dir == Direction.NONE
        cursor.rotate_dir()
        assert cursor.dir == Direction.ACROSS
        cursor.rotate_dir()
        assert cursor.dir == Direction.DOWN
        cursor.rotate_dir()
        assert cursor.dir == Direction.NONE
        cursor.rotate_dir()
        assert cursor.dir == Direction.ACROSS
        cursor.rotate_dir()
        assert cursor.dir == Direction.DOWN
        cursor.rotate_dir()
        assert cursor.dir == Direction.NONE

    def test_rotate_after_assignment(self):
        cursor = Cursor()
        cursor.dir = Direction.DOWN
        cursor.rotate_dir()
        assert cursor.dir == Direction.NONE


def vectors() -> st.SearchStrategy[Vector]:
    return (
        st.builds(Vector, st.lists(st.integers()))
        | st.just(Direction.NONE)
        | st.just(Direction.DOWN)
        | st.just(Direction.ACROSS)
    )


class TestVector:
    @given(x=st.integers(), y=st.integers())
    def test_ctor_of_ints(self, x, y):
        v = Vector(x, y)
        assert v[0] == x
        assert v[1] == y

    @given(st.lists(st.integers()))
    def test_ctor_of_iterable(self, elements):
        v = Vector(elements)
        assert all(a == b for a, b in zip(v, elements))

    def test_empty_ctor(self):
        v = Vector()
        v == ()

    @given(v=vectors())
    def test_truthiness_zero_vector(self, v):
        assert not v.zero

    @given(v=vectors().filter(lambda v: v != v.zero))
    def test_truthiness_any_vector(self, v):
        assert v

    @given(l=st.lists(vectors(), min_size=1))
    def test_hashability(self, l):
        assert set(l)

    @given(u=vectors(), v=vectors(), w=vectors())
    def test_assocativity(self, u, v, w):
        assert u + (v + w) == (u + v) + w

    @given(u=vectors(), v=vectors())
    def test_cumutativity(self, u, v):
        assert u + v == v + u

    @given(v=vectors())
    def test_aditive_identity(self, v):
        assert v + v.zero == v

    @given(v=vectors())
    def test_aditive_inverse(self, v):
        assert v + (-v) == v.zero

    @given(v=vectors())
    def test_scalar_identity(self, v):
        assert 1 * v == v

    @given(a=st.integers(), u=vectors(), v=vectors())
    def test_distributivity_of_multiplication_vaddition(self, a, u, v):
        assert a * (u + v) == a * u + a * v

    @given(a=st.integers(), b=st.integers(), v=vectors())
    def test_distributivity_of_multiplication_saddition(self, a, b, v):
        assert (a + b) * v == a * v + b * v

    @given(a=st.integers(), b=st.integers(), v=vectors())
    def test_scalar_multiplication_and_field_multiplication(self, a, b, v):
        assert a * (b * v) == (a * b) * v
