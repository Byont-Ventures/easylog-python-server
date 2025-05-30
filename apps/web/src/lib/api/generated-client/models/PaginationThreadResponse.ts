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

import { mapValues } from '../runtime';
import type { ThreadResponse } from './ThreadResponse';
import {
  ThreadResponseFromJSON,
  ThreadResponseFromJSONTyped,
  ThreadResponseToJSON,
  ThreadResponseToJSONTyped
} from './ThreadResponse';

/**
 * @export
 * @interface PaginationThreadResponse
 */
export interface PaginationThreadResponse {
  /**
   * @memberof PaginationThreadResponse
   * @type {ThreadResponse[]}
   */
  data: Array<ThreadResponse>;
  /**
   * @memberof PaginationThreadResponse
   * @type {number}
   */
  limit: number;
  /**
   * @memberof PaginationThreadResponse
   * @type {number}
   */
  offset: number;
}

/** Check if a given object implements the PaginationThreadResponse interface. */
export function instanceOfPaginationThreadResponse(
  value: object
): value is PaginationThreadResponse {
  if (!('data' in value) || value['data'] === undefined) return false;
  if (!('limit' in value) || value['limit'] === undefined) return false;
  if (!('offset' in value) || value['offset'] === undefined) return false;
  return true;
}

export function PaginationThreadResponseFromJSON(
  json: any
): PaginationThreadResponse {
  return PaginationThreadResponseFromJSONTyped(json, false);
}

export function PaginationThreadResponseFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): PaginationThreadResponse {
  if (json == null) {
    return json;
  }
  return {
    data: (json['data'] as Array<any>).map(ThreadResponseFromJSON),
    limit: json['limit'],
    offset: json['offset']
  };
}

export function PaginationThreadResponseToJSON(
  json: any
): PaginationThreadResponse {
  return PaginationThreadResponseToJSONTyped(json, false);
}

export function PaginationThreadResponseToJSONTyped(
  value?: PaginationThreadResponse | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    data: (value['data'] as Array<any>).map(ThreadResponseToJSON),
    limit: value['limit'],
    offset: value['offset']
  };
}
