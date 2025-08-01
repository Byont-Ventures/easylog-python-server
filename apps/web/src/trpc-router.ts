import { inferRouterOutputs } from '@trpc/server';

import { createTRPCRouter } from '@/lib/trpc/trpc';

import authRouter from './app/_auth/router';
import chatsRouter from './app/_chats/router';
import documentsRouter from './app/_documents/router';

export const appRouter = createTRPCRouter({
  auth: authRouter,
  documents: documentsRouter,
  chats: chatsRouter
});

export type AppRouter = typeof appRouter;

export type RouterOutputs = inferRouterOutputs<AppRouter>;
