from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from ftw.builder import builder_registry
from ftw.trash.testing import TRASH_FUNCTIONAL
from ftw.trash.tests.builders import DXFolderBuilder
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import sys
import transaction


class FunctionalTestCase(TestCase):
    layer = TRASH_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    @contextmanager
    def user(self, username):
        if hasattr(username, 'getUserName'):
            username = username.getUserName()

        sm = getSecurityManager()
        login(self.layer['portal'], username)
        try:
            yield
        finally:
            setSecurityManager(sm)


def duplicate_with_dexterity(klass):
    """Decorator for duplicating a test suite to be ran against dexterity contents.

    The tests are ran against archetypes by default, meaning that we use the builder
    "folder" as AT builder for the FTI "Folder".
    When using the @duplicate_with_dexterity decorator, an additional class is registered
    (postfixed "Dexterity"), where the "folder" builder is changed to a DX builder
    creating the FTI "dxfolder", which is registered in a Generic Setup test-profile.

    So if you use this decoratior, be aware, that only "Builder('folder')" is replaced
    with dexterity, all other builders and other code does not change.
    """

    class DexterityTestSuite(klass):
        def setUp(self):
            self._builder_isolation = builder_registry.temporary_builder_config()
            self._builder_isolation.__enter__()
            builder_registry.register('folder', DXFolderBuilder, force=True)
            super(DexterityTestSuite, self).setUp()

        def tearDown(self):
            super(DexterityTestSuite, self).tearDown()
            self._builder_isolation.__exit__(None, None, None)
            del self._builder_isolation

    DexterityTestSuite.__name__ = klass.__name__ + 'Dexterity'
    DexterityTestSuite.__module__ = klass.__module__
    sys._getframe(1).f_locals[DexterityTestSuite.__name__] = DexterityTestSuite
    return klass
