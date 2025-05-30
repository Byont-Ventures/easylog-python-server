/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI No description provided (generated by Openapi Generator
 * https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator
 * (https://openapi-generator.tech). https://openapi-generator.tech Do not edit
 * the class manually.
 */

import * as runtime from '../runtime';
import type { HTTPValidationError } from '../models/index';
import {
  HTTPValidationErrorFromJSON,
  HTTPValidationErrorToJSON
} from '../models/index';

export interface UploadDocumentUploadPostRequest {
  file: Blob;
  subject: string;
}

/**
 * KnowledgeApi - interface
 *
 * @export
 * @interface KnowledgeApiInterface
 */
export interface KnowledgeApiInterface {
  /**
   * Upload a PDF document to be processed and stored in the knowledge base
   *
   * @memberof KnowledgeApiInterface
   * @param {Blob} file
   * @param {string} subject
   * @param {any} [options] Override http request option.
   * @throws {RequiredError}
   * @summary Upload Document
   */
  uploadDocumentUploadPostRaw(
    requestParameters: UploadDocumentUploadPostRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<runtime.ApiResponse<any>>;

  /**
   * Upload a PDF document to be processed and stored in the knowledge base
   * Upload Document
   */
  uploadDocumentUploadPost(
    requestParameters: UploadDocumentUploadPostRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<any>;
}

export class KnowledgeApi
  extends runtime.BaseAPI
  implements KnowledgeApiInterface
{
  /**
   * Upload a PDF document to be processed and stored in the knowledge base
   * Upload Document
   */
  async uploadDocumentUploadPostRaw(
    requestParameters: UploadDocumentUploadPostRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<runtime.ApiResponse<any>> {
    if (requestParameters['file'] == null) {
      throw new runtime.RequiredError(
        'file',
        'Required parameter "file" was null or undefined when calling uploadDocumentUploadPost().'
      );
    }

    if (requestParameters['subject'] == null) {
      throw new runtime.RequiredError(
        'subject',
        'Required parameter "subject" was null or undefined when calling uploadDocumentUploadPost().'
      );
    }

    const queryParameters: any = {};

    const headerParameters: runtime.HTTPHeaders = {};

    if (this.configuration && this.configuration.accessToken) {
      const token = this.configuration.accessToken;
      const tokenString = await token('HTTPBearer', []);

      if (tokenString) {
        headerParameters['Authorization'] = `Bearer ${tokenString}`;
      }
    }
    const consumes: runtime.Consume[] = [
      { contentType: 'multipart/form-data' }
    ];
    // @ts-ignore: canConsumeForm may be unused
    const canConsumeForm = runtime.canConsumeForm(consumes);

    let formParams: { append(param: string, value: any): any };
    let useForm = false;
    // use FormData to transmit files using content-type "multipart/form-data"
    useForm = canConsumeForm;
    if (useForm) {
      formParams = new FormData();
    } else {
      formParams = new URLSearchParams();
    }

    if (requestParameters['file'] != null) {
      formParams.append('file', requestParameters['file'] as any);
    }

    if (requestParameters['subject'] != null) {
      formParams.append('subject', requestParameters['subject'] as any);
    }

    const response = await this.request(
      {
        path: `/upload`,
        method: 'POST',
        headers: headerParameters,
        query: queryParameters,
        body: formParams
      },
      initOverrides
    );

    if (this.isJsonMime(response.headers.get('content-type'))) {
      return new runtime.JSONApiResponse<any>(response);
    } else {
      return new runtime.TextApiResponse(response) as any;
    }
  }

  /**
   * Upload a PDF document to be processed and stored in the knowledge base
   * Upload Document
   */
  async uploadDocumentUploadPost(
    requestParameters: UploadDocumentUploadPostRequest,
    initOverrides?: RequestInit | runtime.InitOverrideFunction
  ): Promise<any> {
    const response = await this.uploadDocumentUploadPostRaw(
      requestParameters,
      initOverrides
    );
    return await response.value();
  }
}
