import { BadRequestException, Body, Controller, Delete, Get, Header, HttpCode, Param, Patch, Post, Query, Res } from '@nestjs/common';
import type { Response } from 'express';
import { RequestIdService } from '../shared/request-id.service';
import { RequestTraceService } from '../shared/request-trace.service';
import { GadgetsService } from './gadgets.service';
import { GadgetEntity } from './gadget.entity';
import { CreateGadgetDto } from './dto/create-gadget.dto';
import { UpdateGadgetDto } from './dto/update-gadget.dto';

@Controller('gadgets')
export class GadgetsController {
  constructor(
    private readonly gadgetsService: GadgetsService,
    private readonly requestId: RequestIdService,
    private readonly requestTrace: RequestTraceService,
  ) {}

  private trace(response: Response): void {
    response.setHeader('X-Request-Id', this.requestId.id);
    response.setHeader('X-Request-Trace-Match', String(this.requestId.id === this.requestTrace.getId()));
  }

  @Get()
  @Header('X-API-Version', '1.0')
  @Header('X-Service-Status', 'operational')
  findAll(
    @Query('search') search: string | undefined,
    @Query('limit') rawLimit: string | undefined,
    @Res({ passthrough: true }) response: Response,
  ): GadgetEntity[] {
    this.trace(response);
    const limit = rawLimit === undefined ? undefined : Number(rawLimit);
    if (limit !== undefined && (!Number.isInteger(limit) || limit < 1)) {
      throw new BadRequestException('limit має бути додатним цілим числом');
    }
    return this.gadgetsService.findAll(search, limit);
  }

  @Get(':id')
  findOne(@Param('id') id: string, @Res({ passthrough: true }) response: Response): GadgetEntity {
    this.trace(response);
    return this.gadgetsService.findOne(id);
  }

  @Post()
  create(@Body() dto: CreateGadgetDto, @Res({ passthrough: true }) response: Response): GadgetEntity {
    this.trace(response);
    return this.gadgetsService.create(dto);
  }

  @Patch(':id')
  update(
    @Param('id') id: string,
    @Body() dto: UpdateGadgetDto,
    @Res({ passthrough: true }) response: Response,
  ): GadgetEntity {
    this.trace(response);
    return this.gadgetsService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id') id: string, @Res({ passthrough: true }) response: Response): void {
    this.trace(response);
    this.gadgetsService.remove(id);
  }
}
