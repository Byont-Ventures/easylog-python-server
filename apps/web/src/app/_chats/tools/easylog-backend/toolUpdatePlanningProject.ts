import * as Sentry from '@sentry/nextjs';
import { tool } from 'ai';
import { z } from 'zod';

import { ProjectBody } from '@/lib/easylog/generated-client/models';
import tryCatch from '@/utils/try-catch';

import getEasylogClient from './utils/getEasylogClient';

const toolUpdatePlanningProject = (userId: string) => {
  return tool({
    description: 'Update properties of an existing planning project.',
    inputSchema: z.object({
      projectId: z.number().describe('The ID of the project to update'),
      name: z.string().describe('New name for the project'),
      color: z.string().describe('New color code for the project'),
      reportVisible: z.boolean().describe('Flag to control report visibility'),
      excludeInWorkdays: z
        .boolean()
        .describe('Fflag to exclude project in workday calculations'),
      start: z.string().describe('New start date in YYYY-MM-DD format'),
      end: z.string().describe('New end date in YYYY-MM-DD format'),
      extraData: z
        .object({})
        .catchall(z.union([z.number(), z.string()]))
        .strict()
        .nullable()
        .describe('Optional additional data as a dictionary or JSON string')
    }),
    execute: async ({ projectId, ...updateData }) => {
      const client = await getEasylogClient(userId);

      const projectBody = {
        ...updateData,
        start: new Date(updateData.start),
        end: new Date(updateData.end),
        extraData: updateData.extraData ? updateData.extraData : undefined
      } satisfies ProjectBody;

      const [updatedProjectResponse, error] = await tryCatch(
        client.planning.v2DatasourcesProjectsProjectIdPut({
          projectId,
          projectBody: projectBody as ProjectBody
        })
      );

      if (error) {
        Sentry.captureException(error);
        return `Error updating project: ${error.message}`;
      }

      console.log('updated project', updatedProjectResponse);

      return JSON.stringify(updatedProjectResponse, null, 2);
    }
  });
};

export default toolUpdatePlanningProject;
