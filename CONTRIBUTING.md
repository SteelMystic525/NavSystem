# Contributing to NavSystem

Thank you for taking the time to contribute! The following guidelines help keep the project consistent and the review process smooth.

---

## Getting started

1. **Fork** the repository and clone your fork locally.
2. Create a feature branch from `main`:

   ```bash
   git checkout -b feat/your-feature-name
   ```

3. Make your changes, write tests where applicable, and verify the build:

   ```bash
   cd ~/ros2_ws
   colcon build --packages-select aruco_marker_detection
   colcon test --packages-select aruco_marker_detection
   colcon test-result --verbose
   ```

4. Open a **Pull Request** against `main` with a clear title and description.

---

## Code style

- Follow **PEP 8** for Python code.
- Write **PEP 257**-compliant docstrings for all public classes and functions.
- Run `flake8` before committing:

  ```bash
  flake8 src/aruco_marker_detection
  ```

- Keep lines to **100 characters** or fewer.

---

## Commit messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>

[optional body]
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

Examples:

```
feat(detection): add support for DICT_4X4_50 markers
fix(tf2): handle lookup timeout gracefully
docs(readme): add Gazebo setup instructions
```

---

## Reporting bugs

Please open an issue and include:

- ROS 2 distribution and version (`ros2 --version`)
- Python version (`python3 --version`)
- OpenCV version (`python3 -c "import cv2; print(cv2.__version__)"`)
- Steps to reproduce
- Expected vs. actual behaviour
- Relevant log output

---

## Requesting features

Open an issue with the label `enhancement` describing the use-case and the proposed behaviour.

---

## Licence

By contributing you agree that your contributions will be licensed under the [Apache 2.0 License](LICENSE).
