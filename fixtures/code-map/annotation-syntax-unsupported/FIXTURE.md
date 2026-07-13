> Fixture: targets Dictum v1.1.0. Defect: annotation-syntax-unsupported

One valid `# DICT:` annotation plus two annotations the convention does not
cover: a Lisp-style `;;` comment leader and a lowercase non-grammar ID. The
defect is a mis-written annotation; the tool must extract only the valid one
and surface the other two in `unparsed_annotations` (visible, never silently
dropped).
