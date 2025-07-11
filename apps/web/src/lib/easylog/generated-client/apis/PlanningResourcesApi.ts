/* tslint:disable */
/* eslint-disable */
/**
 * Easylog No description provided (generated by Openapi Generator
 * https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.2.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator
 * (https://openapi-generator.tech). https://openapi-generator.tech Do not edit
 * the class manually.
 */

import * as runtime from '../runtime';
import type {
  V2DatasourcesResourcesGet200Response,
  V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet200Response,
  V2DatasourcesResourcesResourceIdResourceSlugGet200Response
} from '../models/index';
import {
  V2DatasourcesResourcesGet200ResponseFromJSON,
  V2DatasourcesResourcesGet200ResponseToJSON,
  V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet200ResponseFromJSON,
  V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet200ResponseToJSON,
  V2DatasourcesResourcesResourceIdResourceSlugGet200ResponseFromJSON,
  V2DatasourcesResourcesResourceIdResourceSlugGet200ResponseToJSON
} from '../models/index';

export interface V2DatasourcesResourcesResourceIdGetRequest {
  resourceId: number;
}

export interface V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGetRequest {
  resourceId: number;
  datasourceSlug: string;
  startDate?: Date;
  endDate?: Date;
}

export interface V2DatasourcesResourcesResourceIdResourceSlugGetRequest {
  resourceId: number;
  resourceSlug: string;
}

export class PlanningResourcesApi extends runtime.BaseAPI {
  /** Get a list of all resources */
  async v2DatasourcesResourcesGetRaw(
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<runtime.ApiResponse<V2DatasourcesResourcesGet200Response>> {
    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    if (this.configuration && this.configuration.accessToken) {
      const token = this.configuration.accessToken;
      const tokenString = await token('bearer', []);

      if (tokenString) {
        headerParameters['Authorization'] = `Bearer ${tokenString}`;
      }
    }
    const response = await this.request(
      {
        path: `/v2/datasources/resources`,
        method: 'GET',
        headers: headerParameters,
        query: queryParameters
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      V2DatasourcesResourcesGet200ResponseFromJSON(jsonValue)
    );
  }

  /** Get a list of all resources */
  async v2DatasourcesResourcesGet(
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<V2DatasourcesResourcesGet200Response> {
    const response = await this.v2DatasourcesResourcesGetRaw(initOverrides);
    return await response.value();
  }

  /** Get a list of resource groups for a resource */
  async v2DatasourcesResourcesResourceIdGetRaw(
    requestParameters: V2DatasourcesResourcesResourceIdGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<runtime.ApiResponse<V2DatasourcesResourcesGet200Response>> {
    if (requestParameters['resourceId'] == null) {
      throw new runtime.RequiredError(
        'resourceId',
        'Required parameter "resourceId" was null or undefined when calling v2DatasourcesResourcesResourceIdGet().'
      );
    }

    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    if (this.configuration && this.configuration.accessToken) {
      const token = this.configuration.accessToken;
      const tokenString = await token('bearer', []);

      if (tokenString) {
        headerParameters['Authorization'] = `Bearer ${tokenString}`;
      }
    }
    const response = await this.request(
      {
        path: `/v2/datasources/resources/{resourceId}`.replace(
          `{${'resourceId'}}`,
          encodeURIComponent(String(requestParameters['resourceId']))
        ),
        method: 'GET',
        headers: headerParameters,
        query: queryParameters
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      V2DatasourcesResourcesGet200ResponseFromJSON(jsonValue)
    );
  }

  /** Get a list of resource groups for a resource */
  async v2DatasourcesResourcesResourceIdGet(
    requestParameters: V2DatasourcesResourcesResourceIdGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<V2DatasourcesResourcesGet200Response> {
    const response = await this.v2DatasourcesResourcesResourceIdGetRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }

  /** Get a list if all projects of every resource */
  async v2DatasourcesResourcesResourceIdProjectsDatasourceSlugGetRaw(
    requestParameters: V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<
    runtime.ApiResponse<V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet200Response>
  > {
    if (requestParameters['resourceId'] == null) {
      throw new runtime.RequiredError(
        'resourceId',
        'Required parameter "resourceId" was null or undefined when calling v2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet().'
      );
    }

    if (requestParameters['datasourceSlug'] == null) {
      throw new runtime.RequiredError(
        'datasourceSlug',
        'Required parameter "datasourceSlug" was null or undefined when calling v2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet().'
      );
    }

    const queryParameters: any = {};

    if (requestParameters['startDate'] != null) {
      queryParameters['start_date'] = (requestParameters['startDate'] as any)
        .toISOString()
        .substring(0, 10);
    }

    if (requestParameters['endDate'] != null) {
      queryParameters['end_date'] = (requestParameters['endDate'] as any)
        .toISOString()
        .substring(0, 10);
    }

    const headerParameters: runtime.HTTPHeaders = {};

    if (this.configuration && this.configuration.accessToken) {
      const token = this.configuration.accessToken;
      const tokenString = await token('bearer', []);

      if (tokenString) {
        headerParameters['Authorization'] = `Bearer ${tokenString}`;
      }
    }
    const response = await this.request(
      {
        path: `/v2/datasources/resources/{resourceId}/projects/{datasourceSlug}`
          .replace(
            `{${'resourceId'}}`,
            encodeURIComponent(String(requestParameters['resourceId']))
          )
          .replace(
            `{${'datasourceSlug'}}`,
            encodeURIComponent(String(requestParameters['datasourceSlug']))
          ),
        method: 'GET',
        headers: headerParameters,
        query: queryParameters
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet200ResponseFromJSON(
        jsonValue
      )
    );
  }

  /** Get a list if all projects of every resource */
  async v2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet(
    requestParameters: V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<V2DatasourcesResourcesResourceIdProjectsDatasourceSlugGet200Response> {
    const response =
      await this.v2DatasourcesResourcesResourceIdProjectsDatasourceSlugGetRaw(
        requestParameters,
        initOverrides
      );
    return await response.value();
  }

  /** Get a specific resource group for a resource */
  async v2DatasourcesResourcesResourceIdResourceSlugGetRaw(
    requestParameters: V2DatasourcesResourcesResourceIdResourceSlugGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<
    runtime.ApiResponse<V2DatasourcesResourcesResourceIdResourceSlugGet200Response>
  > {
    if (requestParameters['resourceId'] == null) {
      throw new runtime.RequiredError(
        'resourceId',
        'Required parameter "resourceId" was null or undefined when calling v2DatasourcesResourcesResourceIdResourceSlugGet().'
      );
    }

    if (requestParameters['resourceSlug'] == null) {
      throw new runtime.RequiredError(
        'resourceSlug',
        'Required parameter "resourceSlug" was null or undefined when calling v2DatasourcesResourcesResourceIdResourceSlugGet().'
      );
    }

    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    if (this.configuration && this.configuration.accessToken) {
      const token = this.configuration.accessToken;
      const tokenString = await token('bearer', []);

      if (tokenString) {
        headerParameters['Authorization'] = `Bearer ${tokenString}`;
      }
    }
    const response = await this.request(
      {
        path: `/v2/datasources/resources/{resourceId}/{resourceSlug}`
          .replace(
            `{${'resourceId'}}`,
            encodeURIComponent(String(requestParameters['resourceId']))
          )
          .replace(
            `{${'resourceSlug'}}`,
            encodeURIComponent(String(requestParameters['resourceSlug']))
          ),
        method: 'GET',
        headers: headerParameters,
        query: queryParameters
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      V2DatasourcesResourcesResourceIdResourceSlugGet200ResponseFromJSON(
        jsonValue
      )
    );
  }

  /** Get a specific resource group for a resource */
  async v2DatasourcesResourcesResourceIdResourceSlugGet(
    requestParameters: V2DatasourcesResourcesResourceIdResourceSlugGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<V2DatasourcesResourcesResourceIdResourceSlugGet200Response> {
    const response =
      await this.v2DatasourcesResourcesResourceIdResourceSlugGetRaw(
        requestParameters,
        initOverrides
      );
    return await response.value();
  }
}
