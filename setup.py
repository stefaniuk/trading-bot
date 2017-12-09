from setuptools import setup, find_packages

setup(
    name="tradingbot",
    version="v1.0a1",
    packages=find_packages(),
    install_requires=[
        'trading212api',
        'pyyaml',
        'python-telegram-bot'
    ],
    include_package_data=True,
    package_data={'': ['*.conf', 'logs/.null.ini'],
                  'tradingbot.core': ['strategies/*.yml']},
    zip_safe=False,
    author="Federico Lolli",
    author_email="federico123579@gmail.com",
    description="Package to invest Trading212",
    license="MIT",
    keywords="trading bot",
    url="https://github.com/federico123579/TradingBot",
    entry_points={
        'console_scripts': [
            'tradingbot = tradingbot.core.bot:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Emulators'
    ]
)
