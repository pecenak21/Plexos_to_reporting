## EPIC C — Standard Format and file validation

**Components C2 and C5 (checkpoint 1).** Phase 3. Everything upstream of the build converges on one idea: by the time the build script sees a file, it is in Standard Format, and the build **cannot tell** whether that file came from a preprocessor or from a template APS filled in by hand. There is one code path, not two. A filled-in template carries no flag marking it as "new".
