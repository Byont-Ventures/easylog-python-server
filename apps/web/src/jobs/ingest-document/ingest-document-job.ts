import path from 'path';

import { AbortTaskRunError, logger, schemaTask } from '@trigger.dev/sdk';
import { head } from '@vercel/blob';
import { generateObject } from 'ai';
import { eq } from 'drizzle-orm';
import { z } from 'zod';

import db from '@/database/client';
import { documents } from '@/database/schema';
import openrouterProvider from '@/lib/ai-providers/openrouter';
import serverConfig from '@/server.config';

import { processPdfJob } from './converters/process-pdf-job';
import { processXlsxJob } from './converters/process-xlsx-job';

export const ingestDocumentJob = schemaTask({
  id: 'ingest-document',
  schema: z.object({
    documentId: z.string()
  }),
  run: async ({ documentId }) => {
    const dbDocument = await db.query.documents.findFirst({
      where: {
        id: documentId
      }
    });

    if (!dbDocument || !dbDocument.path) {
      throw new AbortTaskRunError('Document not found or path is missing');
    }

    const headResponse = await head(dbDocument.path, {
      token: serverConfig.vercelBlobReadWriteToken
    });

    const contentType = headResponse.contentType;

    const supportedContentTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];

    if (!supportedContentTypes.includes(contentType)) {
      throw new AbortTaskRunError(`Unsupported content type ${contentType}`);
    }

    logger.info('Processing document', {
      filename: dbDocument.name,
      downloadUrl: headResponse.downloadUrl,
      contentType
    });

    const processingResult =
      contentType === 'application/pdf'
        ? await processPdfJob.triggerAndWait({
            downloadUrl: headResponse.downloadUrl,
            basePath: path.dirname(dbDocument.path)
          })
        : await processXlsxJob.triggerAndWait({
            downloadUrl: headResponse.downloadUrl
          });

    if (!processingResult.ok) {
      throw new AbortTaskRunError('Failed to process document');
    }

    logger.info('Processing result', { processingResult });

    const {
      object: { summary, tags }
    } = await generateObject({
      model: openrouterProvider('google/gemini-2.5-flash'),
      prompt: `Act as a professional summarizer. Create a concise and summary of the <text> below, while adhering to the guidelines enclosed in <guidelines> below.

      <guidelines>
        - Ensure that the summary includes relevant details, while avoiding any unnecessary information or repetition. 
        - Rely strictly on the provided text, without including external information.
        - The length of the summary must be within 1000 characters.
        - Your summary must always be in English.
        - Generate tags for unique entities in the text (like people, companies, locations, etc.)
      </guidelines>

      <text>
        ${JSON.stringify(processingResult.output, null, 2)}
      </text>
      `,
      schema: z.object({
        summary: z.string(),
        tags: z.array(z.string())
      })
    });

    logger.info('Summary', { summary, tags });

    const [document] = await db
      .update(documents)
      .set({
        type: contentType === 'application/pdf' ? 'pdf' : 'xlsx',
        summary,
        tags,
        content: processingResult.output
      })
      .where(eq(documents.id, documentId))
      .returning();

    logger.info('Document inserted', { document });
  }
});
