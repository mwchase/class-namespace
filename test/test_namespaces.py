import pytest


def test_import(namespaces):
    assert namespaces


def test_meta_basic(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        pass
    assert Test


def test_basic_namespace(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            a = 1
        assert ns
    assert Test
    assert Test().ns


def test_shadow(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        foo = 1
        with namespaces.Namespace() as ns:
            foo = 2
            assert foo == 2
        assert foo == 1
    assert Test().foo == 1
    assert Test().ns.foo == 2


def test_resume(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        foo = 1
        with namespaces.Namespace() as ns:
            foo = 2
            assert foo == 2
        foo = 3
        with ns:
            foo = 4
        assert foo == 3
    assert Test().foo == 3
    assert Test().ns.foo == 4


def test_redundant_resume(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        foo = 1
        with namespaces.Namespace() as ns:
            foo = 2
            assert foo == 2
        foo = 3
        ns = ns
        with ns as ns:
            foo = 4
        assert foo == 3
    assert Test().foo == 3
    assert Test().ns.foo == 4


def test_basic_inherit(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        foo = 1
        with namespaces.Namespace() as ns:
            foo = 2

    class Subclass(Test):
        pass
    assert Subclass().foo == 1
    assert Subclass().ns.foo == 2


def test_basic_super(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            def hello(self):
                return 1

    class Subclass(Test):
        with namespaces.Namespace() as ns:
            def hello(self):
                return super().ns.hello()

    assert Test().ns.hello() == 1
    assert Subclass().ns.hello() == 1


def test_private(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as __ns:
            foo = 2

        def foo(self):
            return self.__ns.foo

    class Subclass(Test):
        pass

    assert Test().foo() == 2
    assert Subclass().foo() == 2


def test_nested_namespace(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            with namespaces.Namespace() as ns:
                a = 1
    assert Test().ns.ns.a == 1


def test_basic_shadow(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            foo = 2

    class Subclass(Test):
        ns = 1
    assert Subclass().ns == 1


def test_double_shadow(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            foo = 2

    class Subclass(Test):
        ns = 1

    class DoubleSubclass(Subclass):
        with namespaces.Namespace() as ns:
            bar = 1
    assert not hasattr(DoubleSubclass().ns, 'foo')


def test_overlap(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            foo = 2

    class Subclass(Test):
        with namespaces.Namespace() as ns:
            bar = 3
    assert Subclass().ns.foo == 2
    assert Subclass().ns.bar == 3


def test_advanced_overlap(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            foo = 2
            with namespaces.Namespace() as ns:
                qux = 4

    class Subclass(Test):
        with namespaces.Namespace() as ns:
            bar = 3
    assert Subclass().ns.foo == 2
    assert Subclass().ns.bar == 3
    assert Subclass().ns.ns.qux == 4


def test_empty_nameless(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with pytest.raises(namespaces.NamespaceException):
            with namespaces.Namespace():
                pass


def test_non_empty_nameless(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with pytest.raises(namespaces.NamespaceException):
            with namespaces.Namespace():
                a = 1


def test_rename(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            pass
        with pytest.raises(namespaces.namespace_exception(ValueError)):
            with ns as ns2:
                pass


def test_use_namespace(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            foo = 1
        assert ns.foo == 1
        ns.bar = 2
        assert ns.bar == 2
    assert Test.ns.foo == 1
    assert Test.ns.bar == 2


def test_basic_prop(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            @property
            def foo(self):
                return 1
    assert Test().ns.foo == 1


def test_override_method(namespaces):
    class Test(metaclass=namespaces.Namespaceable):
        with namespaces.Namespace() as ns:
            def foo(self):
                return 1
    test = Test()
    assert test.ns.foo() == 1
    test.ns.foo = 2
    print(vars(test))
    assert test.ns.foo == 2
    del test.ns.foo
    assert test.ns.foo() == 1
    Test.ns.foo = 3
    assert Test.ns.foo == 3
    assert test.ns.foo == 3


def test_can_t_preload_with_namespace(namespaces):
    with pytest.raises(namespaces.namespace_exception(ValueError)):
        namespaces.Namespace(ns=namespaces.Namespace())
