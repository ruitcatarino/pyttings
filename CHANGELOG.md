# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Types of changes:
- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.


## [Unreleased](https://github.com/ruitcatarino/pyttings/compare/2.1.0...HEAD)
### Added
- Add option to eager load (opposite of lazy load) the settings
- Add coverage to the Makefile `test` step

## [2.1.0](https://github.com/ruitcatarino/pyttings/compare/2.0.0...2.1.0) - 27-02-2025
### Fixed
- Fixed detection and support for `typing.Union`, ensuring compatibility alongside `|`

## [2.0.0](https://github.com/ruitcatarino/pyttings/compare/1.1.0...2.0.0) - 23-02-2025
### Added
- Type Hint Support: Automatically converts environment variables to their expected types
- Union Type Support: Allows settings to accept multiple possible types
- Collection Type Validation: Ensures list, tuple, set, and dict elements match expected types
- Custom Class Parsers: Supports `__pyttings_convert__` or a user-defined method for parsing settings into custom objects

## [1.1.0](https://github.com/ruitcatarino/pyttings/compare/1.0.0...1.1.0) - 01-02-2025
### Added
- Improved documentation and examples

## [1.0.0](https://github.com/ruitcatarino/pyttings/compare/0.1.0...1.0.0) - 01-02-2025
### Added
- Improved documentation
- Improved the `Makefile`

### Changed
- Changed required python version to 3.10

## [0.1.0](https://github.com/ruitcatarino/pyttings/compare/e94e2b9198c21eb73d13cd9dc63409824883ad50...0.1.0) - 01-02-2025
### Added
- Added class `Settings` and logic associated with it
- Create `Makefile` to make development and testing easier