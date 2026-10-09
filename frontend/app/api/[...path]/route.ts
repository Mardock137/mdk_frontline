import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/session";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const ALLOWED_ROOTS = new Set(["documents", "dashboard"]);

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

function isAllowedPath(segments: string[]): boolean {
  if (segments.length === 0) {
    return false;
  }
  if (!ALLOWED_ROOTS.has(segments[0])) {
    return false;
  }
  return segments.every(
    (segment) => segment.length > 0 && segment !== "." && segment !== "..",
  );
}

async function proxy(
  request: NextRequest,
  context: RouteContext,
): Promise<NextResponse> {
  const { path } = await context.params;
  if (!isAllowedPath(path)) {
    return new NextResponse(null, { status: 404 });
  }

  const destination = `${API_URL}/${path.map((segment) => encodeURIComponent(segment)).join("/")}${request.nextUrl.search}`;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("Content-Type", contentType);
  }

  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE_NAME)?.value;
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const hasBody = request.method === "POST" || request.method === "PATCH";

  let upstream: Response;
  try {
    upstream = await fetch(destination, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      cache: "no-store",
    });
  } catch {
    return new NextResponse(null, { status: 502 });
  }

  if (upstream.status === 204) {
    return new NextResponse(null, { status: 204 });
  }

  const responseHeaders = new Headers();
  const upstreamType = upstream.headers.get("content-type");
  if (upstreamType) {
    responseHeaders.set("Content-Type", upstreamType);
  }

  return new NextResponse(await upstream.arrayBuffer(), {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
