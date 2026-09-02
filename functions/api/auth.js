export async function onRequest(context) {
    const {
        request, 
        env, 
        params, 
        waitUntil, 
        next, 
        data, 
    } = context;

    const client_id = env.GITHUB_CLIENT_ID;

    try {
        const url = new URL(request.url);
        const redirectUrl = new URL('https://github.com/login/oauth/authorize');
        redirectUrl.searchParams.set('client_id', client_id);
        // Ajusta la ruta para que incluya /auth/callback
        redirectUrl.searchParams.set('redirect_uri', url.origin + '/api/auth/callback');
        redirectUrl.searchParams.set('scope', 'repo user');
        redirectUrl.searchParams.set(
            'state',
            crypto.getRandomValues(new Uint8Array(12)).join(''),
        );
        return Response.redirect(redirectUrl.href, 302); // Es mejor usar 302 para redirecciones OAuth temporales

    } catch (error) {
        console.error(error);
        return new Response(error.message, {
            status: 500,
        });
    }
}
