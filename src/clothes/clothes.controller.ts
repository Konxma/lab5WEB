import { BadRequestException, Body, Controller, Delete, Get, HttpCode, Param, Patch, Post, Query, Res } from '@nestjs/common';
import type { Response } from 'express';
import { RequestIdService } from '../shared/request-id.service';
import { RequestTraceService } from '../shared/request-trace.service';
import { ClothesService } from './clothes.service';
import { ClothingEntity } from './clothing.entity';
import { CreateClothingDto } from './dto/create-clothing.dto';
import { UpdateClothingDto } from './dto/update-clothing.dto';

@Controller('clothes')
export class ClothesController {
  constructor(
    private readonly clothesService: ClothesService,
    private readonly requestId: RequestIdService,
    private readonly requestTrace: RequestTraceService,
  ) {}

  private trace(response: Response): void {
    response.setHeader('X-Request-Id', this.requestId.id);
    response.setHeader('X-Request-Trace-Match', String(this.requestId.id === this.requestTrace.getId()));
  }

  @Post()
  create(@Body() dto: CreateClothingDto, @Res({ passthrough: true }) response: Response): ClothingEntity {
    this.trace(response);
    return this.clothesService.create(dto);
  }

  @Get()
  findAll(
    @Query('search') search: string | undefined,
    @Query('limit') rawLimit: string | undefined,
    @Res({ passthrough: true }) response: Response,
  ): ClothingEntity[] {
    this.trace(response);
    const limit = rawLimit === undefined ? undefined : Number(rawLimit);
    if (limit !== undefined && (!Number.isInteger(limit) || limit < 1)) {
      throw new BadRequestException('limit має бути додатним цілим числом');
    }
    return this.clothesService.findAll(search, limit);
  }

  @Get(':id')
  findOne(@Param('id') id: string, @Res({ passthrough: true }) response: Response): ClothingEntity {
    this.trace(response);
    return this.clothesService.findOne(id);
  }

  @Patch(':id')
  update(
    @Param('id') id: string,
    @Body() dto: UpdateClothingDto,
    @Res({ passthrough: true }) response: Response,
  ): ClothingEntity {
    this.trace(response);
    return this.clothesService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id') id: string, @Res({ passthrough: true }) response: Response): void {
    this.trace(response);
    this.clothesService.remove(id);
  }
}
