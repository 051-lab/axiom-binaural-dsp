# Axiom Approval Matrix

| Action | Codex May Do Alone | Requires Pi/Harness | Requires User Approval |
| --- | --- | --- | --- |
| Read repo status and docs | yes | no | no |
| Update docs/session logs | yes | no | before publish only |
| Add Knowledge summary notes | yes | no | no, unless source/privacy is unclear |
| Run static/doc checks | yes | no | no |
| Run real-JDSP measurements | no | yes | task-dependent |
| Create sound-changing candidate | no | yes | yes |
| Record listening acceptance | no | yes | yes |
| Commit local candidate branch | no | yes | after qualification/listening gates |
| Publish PR | no | yes | yes |
| Merge PR | no | yes | separate yes |
| Change accepted baseline policy | no | yes | yes |

## Stop Conditions

- Accepted baseline hash mismatch.
- Historical or accepted EEL file modified in place.
- Normal-material clipping in qualification.
- Silent or unstable host route.
- Unscoped DSP rewrite.
- Private files, paths, audio, manifests, credentials, or protected source text
  entering git.
- External review or Knowledge note treated as proof.
