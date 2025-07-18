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

import { mapValues } from '../runtime';
import type { DatasourceAllocation } from './DatasourceAllocation';
import {
  DatasourceAllocationFromJSON,
  DatasourceAllocationFromJSONTyped,
  DatasourceAllocationToJSON,
  DatasourceAllocationToJSONTyped
} from './DatasourceAllocation';

/**
 * @export
 * @interface V2DatasourcesAllocationsPost201Response
 */
export interface V2DatasourcesAllocationsPost201Response {
  /**
   * @memberof V2DatasourcesAllocationsPost201Response
   * @type {DatasourceAllocation}
   */
  data?: DatasourceAllocation;
}

/**
 * Check if a given object implements the
 * V2DatasourcesAllocationsPost201Response interface.
 */
export function instanceOfV2DatasourcesAllocationsPost201Response(
  value: object
): value is V2DatasourcesAllocationsPost201Response {
  return true;
}

export function V2DatasourcesAllocationsPost201ResponseFromJSON(
  json: any
): V2DatasourcesAllocationsPost201Response {
  return V2DatasourcesAllocationsPost201ResponseFromJSONTyped(json, false);
}

export function V2DatasourcesAllocationsPost201ResponseFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): V2DatasourcesAllocationsPost201Response {
  if (json == null) {
    return json;
  }
  return {
    data:
      json['data'] == null
        ? undefined
        : DatasourceAllocationFromJSON(json['data'])
  };
}

export function V2DatasourcesAllocationsPost201ResponseToJSON(
  json: any
): V2DatasourcesAllocationsPost201Response {
  return V2DatasourcesAllocationsPost201ResponseToJSONTyped(json, false);
}

export function V2DatasourcesAllocationsPost201ResponseToJSONTyped(
  value?: V2DatasourcesAllocationsPost201Response | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    data: DatasourceAllocationToJSON(value['data'])
  };
}
