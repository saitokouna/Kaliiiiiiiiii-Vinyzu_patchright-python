import ast
import glob
import os


def patch_file(file_path: str, patched_tree: ast.AST) -> None:
    with open(file_path, "w") as f:
        f.write(ast.unparse(ast.fix_missing_locations(patched_tree)))

# Patching pyproject.toml
with open("playwright-python/pyproject.toml", "r+") as f:
    pyproject_source = f.read()
    pyproject_source = pyproject_source.replace('version_file = "playwright/_repo_version.py"', 'version_file = "patchright/_repo_version.py"')
    f.seek(0)
    f.write(pyproject_source)
    f.truncate()


# Patching setup.py
with open("playwright-python/setup.py") as f:
    setup_source = f.read()
    setup_tree = ast.parse(setup_source)

    for node in ast.walk(setup_tree):
        # Modify driver_version
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == "driver_version" and node.value.value.startswith("1."):
                node.value.value = node.value.value.split("-")[0]

        # Modify url
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == "url" and node.value.value == "https://playwright.azureedge.net/builds/driver/":
                node.value = ast.JoinedStr(
                    values=[
                        ast.Constant(value='https://github.com/Kaliiiiiiiiii-Vinyzu/patchright/releases/download/v'),
                        ast.FormattedValue(value=ast.Name(id='driver_version', ctx=ast.Load()), conversion=-1),
                        ast.Constant(value='/')
                    ]
                )

        # Modify Curl Call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and len(node.args) >= 1 and isinstance(node.args[0], ast.List) and len(node.args[0].elts) == 4:
            if node.func.value.id == "subprocess" and node.func.attr == "check_call" and node.args[0].elts[0].value == "curl":
                node.args[0].elts.insert(1, ast.Constant(value="-L"))

        # Modify Shutil Call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
            if node.func.value.id == "shutil" and node.func.attr == "rmtree" and node.args[0].value == "playwright.egg-info":
                node.args[0].value = "patchright.egg-info"

        # Modify Os Makedirs Call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
            if node.func.value.id == "os" and node.func.attr == "makedirs" and node.args[0].value == "playwright/driver":
                node.args[0].value = "patchright/driver"

        # Modify Zip Write Call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and len(node.args) >= 2 and isinstance(node.args[1], ast.JoinedStr):
            if node.func.value.id == "zip" and node.func.attr == "write" and node.args[1].values[0].value == "playwright/driver/":
                node.args[1].values[0].value = "patchright/driver/"

        # Modify Zip Writestr Call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
            if node.func.value.id == "zip" and node.func.attr == "writestr" and node.args[0].value == "playwright/driver/README.md":
                node.args[0].value = "patchright/driver/README.md"

        # Modify Extractall Call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            if node.func.id == "extractall" and node.args[1].value == "playwright/driver":
                node.args[1].value = "patchright/driver"

        # Modify Setup Call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "setup":
                for keyword in node.keywords:
                    match keyword.arg:
                        case "name":
                            keyword.value.value = "patchright"
                        case "author":
                            keyword.value.value = "Microsoft Corportation, patched by github.com/Kaliiiiiiiiii-Vinyzu/"
                        case "description":
                            keyword.value.value = "Undetected Python version of the Playwright testing and automation library. "
                        case "url":
                            keyword.value.value = "https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python"
                        case "project_urls":
                            keyword.value = ast.Dict(
                                keys=[
                                    ast.Constant(value='Release notes'), ast.Constant(value='Bug Reports'), ast.Constant(value='Source Code')
                                ],
                                values=[
                                    ast.Constant(value='https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python/releases'),
                                    ast.Constant(value='https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python/issues'),
                                    ast.Constant(value='https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python/')
                                ]
                            )
                        case "packages":
                            keyword.value.elts = [
                                ast.Constant(value='patchright'),
                                ast.Constant(value='patchright.async_api'),
                                ast.Constant(value='patchright.sync_api'),
                                ast.Constant(value='patchright._impl'),
                                ast.Constant(value='patchright._impl.__pyinstaller')
                            ]
                        case "entry_points":
                            keyword.value = ast.Dict(
                                keys=[
                                    ast.Constant(value='console_scripts'),
                                    ast.Constant(value='pyinstaller40')
                                ],
                                values=[
                                    ast.List(elts=[ast.Constant(value='patchright=patchright.__main__:main')], ctx=ast.Load()),
                                    ast.List(elts=[ast.Constant(value='hook-dirs=patchright._impl.__pyinstaller:get_hook_dirs')], ctx=ast.Load())
                                ]
                            )

                node.keywords.append(ast.keyword(
                    arg="version",
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id='os', ctx=ast.Load()),
                                attr='environ', ctx=ast.Load()),
                            attr='get',
                            ctx=ast.Load()),
                        args=[ast.Constant(value="playwright_version")],
                        keywords=[],
                    )
                ))


    patch_file("playwright-python/setup.py", setup_tree)

# Patching playwright/_impl/_driver.py
with open("playwright-python/playwright/_impl/_driver.py") as f:
    driver_source = f.read()
    driver_tree = ast.parse(driver_source)

    for node in ast.walk(driver_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and len(node.args) >= 1 and isinstance(node.args[0], ast.Name):
            if node.func.value.id == "inspect" and node.func.attr == "getfile" and node.args[0].id == "playwright":
                node.args[0].id = "patchright"

    patch_file("playwright-python/playwright/_impl/_driver.py", driver_tree)

# Patching playwright/_impl/_connection.py
with open("playwright-python/playwright/_impl/_connection.py") as f:
    connection_source = f.read()
    connection_source_tree = ast.parse(connection_source)

    for node in ast.walk(connection_source_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) >= 1 and isinstance(node.args[0], ast.Attribute):
            if node.func.id == "Path" and node.args[0].value.id == "playwright":
                node.args[0].value.id = "patchright"

    patch_file("playwright-python/playwright/_impl/_connection.py", connection_source_tree)

# Patching playwright/_impl/_js_handle.py
with open("playwright-python/playwright/_impl/_js_handle.py") as f:
    js_handle_source = f.read()
    js_handle_tree = ast.parse(js_handle_source)

    for node in ast.walk(js_handle_tree):
        if isinstance(node, ast.FunctionDef) and node.name == "add_source_url_to_script":
            for function_node in node.body:
                if isinstance(function_node, ast.Return):
                    function_node.value = ast.Name(id="source", ctx=ast.Load())

    patch_file("playwright-python/playwright/_impl/_js_handle.py", js_handle_tree)

# Patching playwright/_impl/_browser_context.py
with open("playwright-python/playwright/_impl/_browser_context.py") as f:
    browser_context_source = f.read()
    browser_context_tree = ast.parse(browser_context_source)

    for node in ast.walk(browser_context_tree):
        if isinstance(node, ast.ClassDef) and node.name == "BrowserContext":
            for class_node in node.body:
                if isinstance(class_node, ast.AsyncFunctionDef) and class_node.name == "add_init_script":
                    class_node.body.insert(0, ast.parse("await self.install_inject_route()"))
                elif isinstance(class_node, ast.AsyncFunctionDef) and class_node.name == "expose_binding":
                    class_node.body.insert(0, ast.parse("await self.install_inject_route()"))

            node.body.append(
                ast.Assign(
                    targets=[ast.Name(id='route_injecting', ctx=ast.Store())],
                    value=ast.Constant(value=False))
            )

            node.body.append(
                ast.parse("""\
async def install_inject_route(self) -> None:
    from patchright._impl._impl_to_api_mapping import ImplToApiMapping
    mapping = ImplToApiMapping()

    async def route_handler(route: Route) -> None:
            if route.request.resource_type == "document" and route.request.url.startswith("http"):
                try:
                    response = await route.fetch(maxRedirects=0)
                    await route.fulfill(response=response)
                except:
                    await route.continue_()
            else:
                await route.continue_()

    if not self.route_injecting:
        await self.route("**/*", mapping.wrap_handler(route_handler))
        self.route_injecting = True""").body[0])

    patch_file("playwright-python/playwright/_impl/_browser_context.py", browser_context_tree)

# Patching playwright/_impl/_page.py
with open("playwright-python/playwright/_impl/_page.py") as f:
    page_source = f.read()
    page_tree = ast.parse(page_source)

    for node in ast.walk(page_tree):
        if isinstance(node, ast.ClassDef) and node.name == "Page":
            for class_node in node.body:
                if isinstance(class_node, ast.AsyncFunctionDef) and class_node.name == "add_init_script":
                    class_node.body.insert(0, ast.parse("await self.install_inject_route()"))
                elif isinstance(class_node, ast.AsyncFunctionDef) and class_node.name == "expose_binding":
                    class_node.body.insert(0, ast.parse("await self.install_inject_route()"))

            node.body.append(
                ast.Assign(
                    targets=[ast.Name(id='route_injecting', ctx=ast.Store())],
                    value=ast.Constant(value=False))
            )

            node.body.append(
                ast.parse("""\
async def install_inject_route(self) -> None:
    from patchright._impl._impl_to_api_mapping import ImplToApiMapping
    mapping = ImplToApiMapping()
    
    async def route_handler(route: Route) -> None:
            if route.request.resource_type == "document" and route.request.url.startswith("http"):
                try:
                    response = await route.fetch(maxRedirects=0)
                    await route.fulfill(response=response)
                except Exception:
                    await route.continue_()
            else:
                await route.continue_()

    if not self.route_injecting and not self.context.route_injecting:
        await self.route("**/*", mapping.wrap_handler(route_handler))
        self.route_injecting = True""").body[0])

    patch_file("playwright-python/playwright/_impl/_page.py", page_tree)

# Patching playwright/_impl/_clock.py
with open("playwright-python/playwright/_impl/_clock.py") as f:
    clock_source = f.read()
    clock_tree = ast.parse(clock_source)

    for node in ast.walk(clock_tree):
        if isinstance(node, ast.ClassDef) and node.name == "Clock":
            for class_node in node.body:
                if isinstance(class_node, ast.AsyncFunctionDef) and class_node.name == "install":
                    class_node.body.insert(0, ast.parse("await self._browser_context.install_inject_route()"))

    patch_file("playwright-python/playwright/_impl/_clock.py", clock_tree)

# Patching Imports of every python file under the playwright-python/playwright directory
for python_file in glob.glob("playwright-python/playwright/**.py") + glob.glob("playwright-python/playwright/**/**.py"):
    with open(python_file) as f:
        file_source = f.read()
        file_tree = ast.parse(file_source)
        renamed_attributes = []

        for node in ast.walk(file_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("playwright"):
                        if "__init__" in python_file:
                            renamed_attributes.append(alias.name)
                        alias.name = alias.name.replace("playwright", "patchright", 1)
            if isinstance(node, ast.ImportFrom) and node.module.startswith("playwright"):
                node.module = node.module.replace("playwright", "patchright", 1)
            if renamed_attributes and isinstance(node, ast.Attribute):
                unparsed_attribute = ast.unparse(node.value)
                if unparsed_attribute in renamed_attributes:
                    node.value = ast.parse(unparsed_attribute.replace("playwright", "patchright", 1)).body[0].value

        patch_file(python_file, file_tree)

# Rename the Package Folder to Patchright
os.rename("playwright-python/playwright", "playwright-python/patchright")

# Write the Projects README to the README which is used in the release
with open("README.md", 'r') as src:
    with open("playwright-python/README.md", 'w') as dst:
        # Read from the source readme and write to the destination readme
        dst.write(src.read())
