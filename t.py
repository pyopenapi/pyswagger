import unittest
from pyswagger.tests.test_render import ObjectTestCase as t


if __name__ == '__main__':
    import logging
    logger = logging.getLogger('pyswagger')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    logger.addHandler(console)
    logger.setLevel(logging.ERROR)

    unittest.TextTestRunner().run(
        unittest.makeSuite(t, 'test_')
    )

