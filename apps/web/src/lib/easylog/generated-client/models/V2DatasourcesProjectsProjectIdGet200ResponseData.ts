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
import type { AllocationTypesAllocationTypesInner } from './AllocationTypesAllocationTypesInner';
import {
  AllocationTypesAllocationTypesInnerFromJSON,
  AllocationTypesAllocationTypesInnerFromJSONTyped,
  AllocationTypesAllocationTypesInnerToJSON,
  AllocationTypesAllocationTypesInnerToJSONTyped
} from './AllocationTypesAllocationTypesInner';
import type { AllocationsGrouped } from './AllocationsGrouped';
import {
  AllocationsGroupedFromJSON,
  AllocationsGroupedFromJSONTyped,
  AllocationsGroupedToJSON,
  AllocationsGroupedToJSONTyped
} from './AllocationsGrouped';

/**
 * @export
 * @interface V2DatasourcesProjectsProjectIdGet200ResponseData
 */
export interface V2DatasourcesProjectsProjectIdGet200ResponseData {
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {number}
   */
  id?: number;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {number}
   */
  datasourceId?: number | null;
  /**
   * Use this field to display to the user
   *
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {string}
   */
  label?: string;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {string}
   */
  name?: string;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {Date}
   */
  start?: Date;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {Date}
   */
  end?: Date;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {string}
   */
  color?: string;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {object}
   */
  extraData?: object | null;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {AllocationTypesAllocationTypesInner[]}
   */
  allocationTypes?: Array<AllocationTypesAllocationTypesInner> | null;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {Date}
   */
  createdAt?: Date;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {Date}
   */
  updatedAt?: Date;
  /**
   * @memberof V2DatasourcesProjectsProjectIdGet200ResponseData
   * @type {AllocationsGrouped[]}
   */
  allocationsGrouped?: Array<AllocationsGrouped>;
}

/**
 * Check if a given object implements the
 * V2DatasourcesProjectsProjectIdGet200ResponseData interface.
 */
export function instanceOfV2DatasourcesProjectsProjectIdGet200ResponseData(
  value: object
): value is V2DatasourcesProjectsProjectIdGet200ResponseData {
  return true;
}

export function V2DatasourcesProjectsProjectIdGet200ResponseDataFromJSON(
  json: any
): V2DatasourcesProjectsProjectIdGet200ResponseData {
  return V2DatasourcesProjectsProjectIdGet200ResponseDataFromJSONTyped(
    json,
    false
  );
}

export function V2DatasourcesProjectsProjectIdGet200ResponseDataFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): V2DatasourcesProjectsProjectIdGet200ResponseData {
  if (json == null) {
    return json;
  }
  return {
    id: json['id'] == null ? undefined : json['id'],
    datasourceId:
      json['datasource_id'] == null ? undefined : json['datasource_id'],
    label: json['label'] == null ? undefined : json['label'],
    name: json['name'] == null ? undefined : json['name'],
    start: json['start'] == null ? undefined : new Date(json['start']),
    end: json['end'] == null ? undefined : new Date(json['end']),
    color: json['color'] == null ? undefined : json['color'],
    extraData: json['extra_data'] == null ? undefined : json['extra_data'],
    allocationTypes:
      json['allocation_types'] == null
        ? undefined
        : (json['allocation_types'] as Array<any>).map(
            AllocationTypesAllocationTypesInnerFromJSON
          ),
    createdAt:
      json['created_at'] == null ? undefined : new Date(json['created_at']),
    updatedAt:
      json['updated_at'] == null ? undefined : new Date(json['updated_at']),
    allocationsGrouped:
      json['allocations_grouped'] == null
        ? undefined
        : (json['allocations_grouped'] as Array<any>).map(
            AllocationsGroupedFromJSON
          )
  };
}

export function V2DatasourcesProjectsProjectIdGet200ResponseDataToJSON(
  json: any
): V2DatasourcesProjectsProjectIdGet200ResponseData {
  return V2DatasourcesProjectsProjectIdGet200ResponseDataToJSONTyped(
    json,
    false
  );
}

export function V2DatasourcesProjectsProjectIdGet200ResponseDataToJSONTyped(
  value?: V2DatasourcesProjectsProjectIdGet200ResponseData | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    id: value['id'],
    datasource_id: value['datasourceId'],
    label: value['label'],
    name: value['name'],
    start: value['start'] == null ? undefined : value['start'].toISOString(),
    end: value['end'] == null ? undefined : value['end'].toISOString(),
    color: value['color'],
    extra_data: value['extraData'],
    allocation_types:
      value['allocationTypes'] == null
        ? undefined
        : (value['allocationTypes'] as Array<any>).map(
            AllocationTypesAllocationTypesInnerToJSON
          ),
    created_at:
      value['createdAt'] == null ? undefined : value['createdAt'].toISOString(),
    updated_at:
      value['updatedAt'] == null ? undefined : value['updatedAt'].toISOString(),
    allocations_grouped:
      value['allocationsGrouped'] == null
        ? undefined
        : (value['allocationsGrouped'] as Array<any>).map(
            AllocationsGroupedToJSON
          )
  };
}
