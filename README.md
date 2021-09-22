# mde-toolkit

Collection of tools useful for Virginia Tech ECE MDE course administration.

## Canvas Development Guide

### Basics

- Need access token from Canvas directly. See guide on how to manually request a token: <https://kb.iu.edu/d/aaja>
- Save access token to environment variable `CANVAS_API_TOKEN`
- Canvas API documentation <https://canvas.instructure.com/doc/api/>
- Use `jq` to filter JSON responses
- Canvas API uses pagination (limit is 10 results per query). This can be extended using the `?per_page=100` query modifier.

### Query Examples

Basic query to get list of courses:

```bash
curl -H "Authorization: Bearer ${CANVAS_API_TOKEN}" "https://canvas.vt.edu/api/v1/courses?per_page=100"
```
