# PyStudio Python Runner

The recommended runner endpoint is now `/api/run` at the project root. It uses
Vercel Sandbox to execute submitted Python code in a short-lived, isolated
microVM rather than executing it on the website visitor's phone.

## Deployment notes

1. Import this GitHub repository into Vercel (or redeploy the existing project).
2. Ensure the project is using a current Node.js runtime and has access to
   Vercel Sandbox. The `@vercel/sandbox` package is declared in root
   `package.json`; Sandbox authentication is provided automatically in
   production on Vercel.
3. In Vercel Project Settings, set `ALLOWED_ORIGINS` to the exact production
   website origin, for example `https://your-project.vercel.app`. This is
   an optional extra origin check, not authentication or a complete abuse
   prevention system.
4. Deploy and test `/api/run` with a small Python program that prints output.
5. Add a managed rate limit/abuse protection before inviting public users.

The API currently executes Python 3.13 in an isolated Sandbox, limits submitted
code to 12,000 characters, truncates output, and requests a 30-second sandbox
timeout. This first version does not preinstall all PyPI packages. Common
scientific libraries and arbitrary `pip install` support need a separate
dependency strategy and testing. Never promise compatibility with every PyPI
package.

Do not expose secrets in frontend code. Sandbox usage and deployments may incur
charges depending on the Vercel plan and workload.
