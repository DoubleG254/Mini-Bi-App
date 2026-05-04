import { Navigate } from "@solidjs/router";
import { type ParentProps, Show } from "solid-js";
import { isAuthenticated } from "../lib/auth";

type GuardProps = ParentProps;

export function ProtectedRoute(props: GuardProps) {
  return (
    <Show
      when={isAuthenticated()}
      fallback={<Navigate href="/" />}
    >
      {props.children}
    </Show>
  );
}

export function PublicRoute(props: GuardProps) {
  return (
    <Show when={!isAuthenticated()} fallback={<Navigate href="/dashboard" />}>
      {props.children}
    </Show>
  );
}