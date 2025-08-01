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
import type { DatasourceExtraDataFieldsInnerOptionsInner } from './DatasourceExtraDataFieldsInnerOptionsInner';
import {
  DatasourceExtraDataFieldsInnerOptionsInnerFromJSON,
  DatasourceExtraDataFieldsInnerOptionsInnerFromJSONTyped,
  DatasourceExtraDataFieldsInnerOptionsInnerToJSON,
  DatasourceExtraDataFieldsInnerOptionsInnerToJSONTyped
} from './DatasourceExtraDataFieldsInnerOptionsInner';

/**
 * @export
 * @interface DatasourceExtraDataFieldsInner
 */
export interface DatasourceExtraDataFieldsInner {
  /**
   * @memberof DatasourceExtraDataFieldsInner
   * @type {string}
   */
  name?: string;
  /**
   * @memberof DatasourceExtraDataFieldsInner
   * @type {string}
   */
  type?: string;
  /**
   * @memberof DatasourceExtraDataFieldsInner
   * @type {string}
   */
  label?: string;
  /**
   * @memberof DatasourceExtraDataFieldsInner
   * @type {DatasourceExtraDataFieldsInnerOptionsInner[]}
   */
  options?: Array<DatasourceExtraDataFieldsInnerOptionsInner>;
}

/**
 * Check if a given object implements the DatasourceExtraDataFieldsInner
 * interface.
 */
export function instanceOfDatasourceExtraDataFieldsInner(
  value: object
): value is DatasourceExtraDataFieldsInner {
  return true;
}

export function DatasourceExtraDataFieldsInnerFromJSON(
  json: any
): DatasourceExtraDataFieldsInner {
  return DatasourceExtraDataFieldsInnerFromJSONTyped(json, false);
}

export function DatasourceExtraDataFieldsInnerFromJSONTyped(
  json: any,
  ignoreDiscriminator: boolean
): DatasourceExtraDataFieldsInner {
  if (json == null) {
    return json;
  }
  return {
    name: json['name'] == null ? undefined : json['name'],
    type: json['type'] == null ? undefined : json['type'],
    label: json['label'] == null ? undefined : json['label'],
    options:
      json['options'] == null
        ? undefined
        : (json['options'] as Array<any>).map(
            DatasourceExtraDataFieldsInnerOptionsInnerFromJSON
          )
  };
}

export function DatasourceExtraDataFieldsInnerToJSON(
  json: any
): DatasourceExtraDataFieldsInner {
  return DatasourceExtraDataFieldsInnerToJSONTyped(json, false);
}

export function DatasourceExtraDataFieldsInnerToJSONTyped(
  value?: DatasourceExtraDataFieldsInner | null,
  ignoreDiscriminator: boolean = false
): any {
  if (value == null) {
    return value;
  }

  return {
    name: value['name'],
    type: value['type'],
    label: value['label'],
    options:
      value['options'] == null
        ? undefined
        : (value['options'] as Array<any>).map(
            DatasourceExtraDataFieldsInnerOptionsInnerToJSON
          )
  };
}
