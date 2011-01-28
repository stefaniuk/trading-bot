from setuptools import setup, find_packages

setup(
    name="tradingbot",
    version="1.0a1",
    packages=['tradingbot', 'tradingbot.core'],
    install_requires=[
        'trading212api'
    ],
    include_package_data=True,
    package_data={'': ['*.conf']},
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Emulators'
    ]
)
