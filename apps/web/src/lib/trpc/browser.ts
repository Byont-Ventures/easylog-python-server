'use client';

import { createTRPCContext } from '@trpc/tanstack-react-query';

import type { AppRouter } from '@/trpc-router';

const { TRPCProvider, useTRPC, useTRPCClient } = createTRPCContext<AppRouter>();

export { TRPCProvider, useTRPCClient };

export default useTRPC;
