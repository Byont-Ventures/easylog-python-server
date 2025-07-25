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
  V2ConfigurationGet200Response,
  V2DatasourcesClientClientIdConfigurationGet200Response
} from '../models/index';
import {
  V2ConfigurationGet200ResponseFromJSON,
  V2ConfigurationGet200ResponseToJSON,
  V2DatasourcesClientClientIdConfigurationGet200ResponseFromJSON,
  V2DatasourcesClientClientIdConfigurationGet200ResponseToJSON
} from '../models/index';

export interface V2DatasourcesClientClientIdConfigurationGetRequest {
  clientId: string;
}

export class DefaultApi extends runtime.BaseAPI {
  /** Get the configuration for the frontend Get configuration */
  async v2ConfigurationGetRaw(
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<runtime.ApiResponse<V2ConfigurationGet200Response>> {
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
        path: `/v2/configuration`,
        method: 'GET',
        headers: headerParameters,
        query: queryParameters
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      V2ConfigurationGet200ResponseFromJSON(jsonValue)
    );
  }

  /** Get the configuration for the frontend Get configuration */
  async v2ConfigurationGet(
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<V2ConfigurationGet200Response> {
    const response = await this.v2ConfigurationGetRaw(initOverrides);
    return await response.value();
  }

  /**
   * Get the configuration for the frontend Get configuration
   *
   * @deprecated
   */
  async v2DatasourcesClientClientIdConfigurationGetRaw(
    requestParameters: V2DatasourcesClientClientIdConfigurationGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<
    runtime.ApiResponse<V2DatasourcesClientClientIdConfigurationGet200Response>
  > {
    if (requestParameters['clientId'] == null) {
      throw new runtime.RequiredError(
        'clientId',
        'Required parameter "clientId" was null or undefined when calling v2DatasourcesClientClientIdConfigurationGet().'
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
        path: `/v2/datasources/client/{clientId}/configuration`.replace(
          `{${'clientId'}}`,
          encodeURIComponent(String(requestParameters['clientId']))
        ),
        method: 'GET',
        headers: headerParameters,
        query: queryParameters
      },
      initOverrides
    );

    return new runtime.JSONApiResponse(response, (jsonValue) =>
      V2DatasourcesClientClientIdConfigurationGet200ResponseFromJSON(jsonValue)
    );
  }

  /**
   * Get the configuration for the frontend Get configuration
   *
   * @deprecated
   */
  async v2DatasourcesClientClientIdConfigurationGet(
    requestParameters: V2DatasourcesClientClientIdConfigurationGetRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<V2DatasourcesClientClientIdConfigurationGet200Response> {
    const response = await this.v2DatasourcesClientClientIdConfigurationGetRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }
}
