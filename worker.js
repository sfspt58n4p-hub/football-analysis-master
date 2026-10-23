const UPSTREAM = "https://cp.nowscore.com/buy/Jingcai.aspx?TypeID=105&OddsType=2";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/fixtures") {
      if (request.method !== "GET") {
        return new Response("Method not allowed", { status: 405 });
      }

      try {
        const upstream = await fetch(UPSTREAM, {
          method: "GET",
          headers: {
            "User-Agent": "Mozilla/5.0 (compatible; FootballAnalysis/1.0)",
            "Accept": "text/html,application/xhtml+xml"
          },
          redirect: "follow"
        });

        const body = await upstream.text();
        return new Response(body, {
          status: upstream.status,
          headers: {
            "Content-Type": upstream.headers.get("content-type") || "text/html; charset=utf-8",
            "Cache-Control": "no-store",
            "X-Fixture-Proxy": "nowscore"
          }
        });
      } catch (error) {
        return new Response("捷报代理请求失败：" + String(error), {
          status: 502,
          headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" }
        });
      }
    }

    return env.ASSETS.fetch(request);
  }
};
