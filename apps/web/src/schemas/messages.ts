import { z } from 'zod';

export const textDeltaContentSchema = z.object({
  id: z.string(),
  type: z.literal('text_delta'),
  delta: z.string()
});

export const textContentSchema = z.object({
  id: z.string(),
  type: z.literal('text'),
  text: z.string()
});

export const toolUseContentSchema = z.object({
  id: z.string(),
  type: z.literal('tool_use'),
  tool_use_id: z.string(),
  name: z.string(),
  input: z.record(z.any())
});

export const toolResultContentSchema = z.object({
  id: z.string(),
  type: z.literal('tool_result'),
  tool_use_id: z.string(),
  output: z.string(),
  widget_type: z
    .enum(['text', 'image', 'image_url', 'chart', 'multiple_choice'])
    .nullish(),
  is_error: z.boolean()
});

export const imageContentSchema = z.object({
  id: z.string(),
  type: z.literal('image'),
  image_url: z.string()
});

export const fileContentSchema = z.object({
  id: z.string(),
  type: z.literal('file'),
  file_data: z.string(),
  file_name: z.string()
});

export const messageContentSchema = z.discriminatedUnion('type', [
  textContentSchema,
  textDeltaContentSchema,
  toolUseContentSchema,
  toolResultContentSchema,
  imageContentSchema,
  fileContentSchema
]);

export type MessageContent = z.infer<typeof messageContentSchema>;

export const messageSchema = z.object({
  id: z.string(),
  role: z.enum(['user', 'assistant', 'system', 'developer', 'tool']),
  name: z.string().nullish(),
  tool_use_id: z.string().nullish(),
  content: z.array(messageContentSchema)
});

export type Message = z.infer<typeof messageSchema>;

export const messageDeltaSchema = z.object({
  chunk_id: z.number(),
  delta: z.string()
});

export type MessageDelta = z.infer<typeof messageDeltaSchema>;
